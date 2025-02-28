from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db import models
from .models import Proyecto, Tarea, Comentario, Mensaje, PerfilProyecto, Grupo, Notificacion, User
from .forms import (
    ProyectoForm, TareaForm, MensajeForm, ComentarioForm, GrupoForm, 
    AsignarUsuarioGrupoForm, CrearUsuarioForm
)
from django.conf import settings

# Vista para listar proyectos
@login_required
def lista_proyectos(request):
    """Muestra la lista de proyectos asociados al usuario a través de grupos."""
    proyectos = Proyecto.objects.filter(
        grupos__miembros=request.user
    ).distinct().select_related('creado_por')
    return render(request, 'core/lista_proyectos.html', {'proyectos': proyectos})

# Función auxiliar para verificar permisos
def es_admin_o_superusuario(user):
    """Comprueba si el usuario es superusuario o administrador en algún proyecto."""
    return user.is_superuser or PerfilProyecto.objects.filter(
        usuario=user, rol='administrador'
    ).exists()

# Vista para crear un usuario
@login_required
@user_passes_test(es_admin_o_superusuario, login_url='lista_proyectos')
def crear_usuario(request):
    """Permite a administradores o superusuarios crear nuevos usuarios."""
    if request.method == 'POST':
        form = CrearUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f"Usuario '{usuario.username}' creado exitosamente.")
            return redirect('lista_proyectos')
        else:
            messages.error(request, "Error al crear el usuario. Revisa los datos ingresados.")
    else:
        form = CrearUsuarioForm()
        if not request.user.is_superuser:
            proyectos_admin = Proyecto.objects.filter(
                perfilproyecto__usuario=request.user, 
                perfilproyecto__rol='administrador'
            )
            form.fields['proyecto'].queryset = proyectos_admin
    return render(request, 'core/crear_usuario.html', {'form': form})

# Vista para crear un proyecto
@login_required
def crear_proyecto(request):
    """Crea un nuevo proyecto y lo asocia a grupos existentes."""
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proyecto = form.save(commit=False)
            proyecto.creado_por = request.user
            proyecto.save()
            grupos = form.cleaned_data['grupos']
            for grupo in grupos:
                grupo.proyecto = proyecto
                grupo.save()
            PerfilProyecto.objects.create(
                usuario=request.user, 
                proyecto=proyecto, 
                grupo=grupos[0], 
                rol='administrador'
            )
            # Solo generar notificación si no existe una similar
            if not Notificacion.objects.filter(
                usuario=request.user,
                mensaje__contains=f"Has creado y sido asignado al proyecto '{proyecto.titulo}'",
                proyecto=proyecto
            ).exists():
                Notificacion.objects.create(
                    usuario=request.user,
                    mensaje=f"Has creado y sido asignado al proyecto '{proyecto.titulo}'",
                    proyecto=proyecto
                )
            messages.success(request, f"Proyecto '{proyecto.titulo}' creado exitosamente.")
            return redirect('lista_proyectos')
        else:
            messages.error(request, "Error al crear el proyecto. Verifica los datos.")
    else:
        form = ProyectoForm()
    return render(request, 'core/crear_proyecto.html', {'form': form})

# Vista para listar tareas de un proyecto
@login_required
def lista_tareas(request, proyecto_id):
    """Lista las tareas de un proyecto al que el usuario tiene acceso a través de grupos."""
    proyecto = get_object_or_404(
        Proyecto.objects.filter(grupos__miembros=request.user).select_related('creado_por'), 
        id=proyecto_id
    )
    tareas = Tarea.objects.filter(proyecto=proyecto).prefetch_related('usuarios_asignados')
    estado = request.GET.get('estado')
    usuario_asignado = request.GET.get('usuario')
    if estado:
        tareas = tareas.filter(estado=estado)
    if usuario_asignado:
        tareas = tareas.filter(usuarios_asignados__id=usuario_asignado)
    usuarios_proyecto = User.objects.filter(grupos__proyecto=proyecto).distinct()
    return render(request, 'core/lista_tareas.html', {
        'proyecto': proyecto, 
        'tareas': tareas, 
        'usuarios_proyecto': usuarios_proyecto
    })

# Vista para crear una tarea
@login_required
def crear_tarea(request, proyecto_id):
    proyecto = get_object_or_404(
        Proyecto.objects.filter(grupos__miembros=request.user), 
        id=proyecto_id
    )
    if request.method == 'POST':
        form = TareaForm(request.POST, proyecto=proyecto)
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.proyecto = proyecto
            tarea.save()
            tarea.usuarios_asignados.add(request.user)
            for usuario in tarea.usuarios_asignados.all():
                if not Notificacion.objects.filter(
                    usuario=usuario,
                    mensaje__contains=f"Te han asignado la tarea '{tarea.titulo}'",
                    proyecto=proyecto
                ).exists():
                    Notificacion.objects.create(
                        usuario=usuario,
                        mensaje=f"Te han asignado la tarea '{tarea.titulo}' en el proyecto '{proyecto.titulo}'",
                        proyecto=proyecto
                    )
            messages.success(request, f"Tarea '{tarea.titulo}' creada exitosamente.")
            return redirect('lista_tareas', proyecto_id=proyecto.id)
        else:
            messages.error(request, "Error al crear la tarea. Verifica los datos.")
    else:
        form = TareaForm(proyecto=proyecto)
    return render(request, 'core/crear_tarea.html', {'form': form, 'proyecto': proyecto})

# Vista para editar un proyecto
@login_required
def editar_proyecto(request, proyecto_id):
    """Edita un proyecto existente, restringido a administradores, creadores o superusuarios."""
    proyecto = get_object_or_404(
        Proyecto.objects.filter(grupos__miembros=request.user), 
        id=proyecto_id
    )
    es_admin = PerfilProyecto.objects.filter(
        usuario=request.user, proyecto=proyecto, rol='administrador'
    ).exists()
    es_creador = proyecto.creado_por == request.user
    es_superusuario = request.user.is_superuser
    if not (es_admin or es_creador or es_superusuario):
        messages.warning(request, "No tienes permiso para editar este proyecto.")
        return redirect('lista_proyectos')
    if request.method == 'POST':
        form = ProyectoForm(request.POST, instance=proyecto)
        if form.is_valid():
            form.save()
            messages.success(request, f"Proyecto '{proyecto.titulo}' actualizado exitosamente.")
            return redirect('lista_proyectos')
        else:
            messages.error(request, "Error al actualizar el proyecto. Verifica los datos.")
    else:
        form = ProyectoForm(instance=proyecto)
    return render(request, 'core/editar_proyecto.html', {'form': form, 'proyecto': proyecto})

# Vista para editar una tarea
def editar_tarea(request, proyecto_id, tarea_id):
    proyecto = get_object_or_404(Proyecto.objects.filter(grupos__miembros=request.user), id=proyecto_id)
    tarea = get_object_or_404(Tarea, id=tarea_id, proyecto=proyecto)
    tarea = get_object_or_404(Tarea, id=tarea_id, proyecto=proyecto)
    es_admin = PerfilProyecto.objects.filter(
        usuario=request.user, proyecto=proyecto, rol='administrador'
    ).exists()
    es_asignado = tarea.usuarios_asignados.filter(id=request.user.id).exists()
    es_superusuario = request.user.is_superuser
    if not (es_admin or es_asignado or es_superusuario):
        messages.warning(request, "No tienes permiso para editar esta tarea.")
        return redirect('lista_tareas', proyecto_id=proyecto.id)
    if request.method == 'POST':
        form = TareaForm(request.POST, instance=tarea, proyecto=proyecto)
        if form.is_valid():
            form.save()
            for usuario in tarea.usuarios_asignados.exclude(id=request.user.id):
                Notificacion.objects.create(
                    usuario=usuario,
                    mensaje=f"La tarea '{tarea.titulo}' en el proyecto '{proyecto.titulo}' ha sido modificada",
                    proyecto=proyecto
                )
            messages.success(request, f"Tarea '{tarea.titulo}' actualizada exitosamente.")
            return redirect('lista_tareas', proyecto_id=proyecto.id)
        else:
            messages.error(request, "Error al actualizar la tarea. Verifica los datos.")
    else:
        form = TareaForm(instance=tarea, proyecto=proyecto)
    return render(request, 'core/editar_tarea.html', {'form': form, 'proyecto': proyecto, 'tarea': tarea})

# Vista para mensajes en un proyecto
@login_required
def mensajes_proyecto(request, proyecto_id):
    """Muestra y envía mensajes dentro de un proyecto específico."""
    proyecto = get_object_or_404(
        Proyecto.objects.filter(grupos__miembros=request.user).select_related('creado_por'), 
        id=proyecto_id
    )
    mensajes = Mensaje.objects.filter(
        proyecto=proyecto
    ).filter(
        models.Q(remitente=request.user) | models.Q(destinatario=request.user)
    ).select_related('remitente', 'destinatario').order_by('fecha_hora')
    
    if request.method == 'POST':
        form = MensajeForm(request.POST, proyecto=proyecto, usuario=request.user)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.proyecto = proyecto
            mensaje.remitente = request.user
            mensaje.save()
            Notificacion.objects.create(
                usuario=mensaje.destinatario,
                mensaje=f"Has recibido un mensaje de {mensaje.remitente} en el proyecto '{proyecto.titulo}'",
                proyecto=proyecto
            )
            messages.success(request, f"Mensaje enviado a '{mensaje.destinatario.username}'.")
            return redirect('mensajes_proyecto', proyecto_id=proyecto.id)
        else:
            messages.error(request, "Error al enviar el mensaje. Verifica los datos.")
    else:
        form = MensajeForm(proyecto=proyecto, usuario=request.user)
    return render(request, 'core/mensajes_proyecto.html', {
        'proyecto': proyecto, 
        'mensajes': mensajes, 
        'form': form
    })

# Vista para comentarios en una tarea
@login_required
def comentarios_tarea(request, proyecto_id, tarea_id):
    """Muestra y permite añadir comentarios a una tarea específica."""
    proyecto = get_object_or_404(
        Proyecto.objects.filter(grupos__miembros=request.user), 
        id=proyecto_id
    )
    tarea = get_object_or_404(Tarea, id=tarea_id, proyecto=proyecto)
    comentarios = Comentario.objects.filter(tarea=tarea).select_related('usuario').order_by('fecha_hora')
    
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.tarea = tarea
            comentario.usuario = request.user
            comentario.save()
            for usuario in tarea.usuarios_asignados.exclude(id=request.user.id):
                Notificacion.objects.create(
                    usuario=usuario,
                    mensaje=f"Nuevo comentario en la tarea '{tarea.titulo}' por {request.user.username}",
                    proyecto=proyecto
                )
            messages.success(request, "Comentario añadido exitosamente.")
            return redirect('comentarios_tarea', proyecto_id=proyecto.id, tarea_id=tarea.id)
        else:
            messages.error(request, "Error al añadir el comentario. Verifica el contenido.")
    else:
        form = ComentarioForm()
    return render(request, 'core/comentarios_tarea.html', {
        'proyecto': proyecto, 
        'tarea': tarea, 
        'comentarios': comentarios, 
        'form': form
    })

# Vista para gestionar grupos en un proyecto
@login_required
def gestionar_grupos(request, proyecto_id):
    """Permite a administradores crear y listar grupos en un proyecto."""
    proyecto = get_object_or_404(
        Proyecto.objects.filter(grupos__miembros=request.user), 
        id=proyecto_id
    )
    es_admin = PerfilProyecto.objects.filter(
        usuario=request.user, proyecto=proyecto, rol='administrador'
    ).exists()
    es_superusuario = request.user.is_superuser
    if not (es_admin or es_superusuario):
        messages.warning(request, "No tienes permiso para gestionar grupos en este proyecto.")
        return redirect('lista_proyectos')
    
    grupos = Grupo.objects.filter(proyecto=proyecto)
    if request.method == 'POST':
        form = GrupoForm(request.POST)
        if form.is_valid():
            grupo = form.save(commit=False)
            grupo.proyecto = proyecto
            grupo.save()
            messages.success(request, f"Grupo '{grupo.nombre}' creado exitosamente.")
            return redirect('gestionar_grupos', proyecto_id=proyecto.id)
        else:
            messages.error(request, "Error al crear el grupo. Verifica el nombre.")
    else:
        form = GrupoForm()
    return render(request, 'core/gestionar_grupos.html', {
        'proyecto': proyecto, 
        'grupos': grupos, 
        'form': form
    })

# Vista para asignar usuarios a un grupo
@login_required
def asignar_usuario_grupo(request, proyecto_id, grupo_id):
    """Asigna usuarios a un grupo dentro de un proyecto y muestra los miembros actuales."""
    proyecto = get_object_or_404(
        Proyecto.objects.filter(grupos__miembros=request.user), 
        id=proyecto_id
    )
    grupo = get_object_or_404(Grupo, id=grupo_id, proyecto=proyecto)
    es_admin = PerfilProyecto.objects.filter(
        usuario=request.user, proyecto=proyecto, rol='administrador'
    ).exists()
    if not es_admin:
        messages.warning(request, "No tienes permiso para asignar usuarios a este grupo.")
        return redirect('gestionar_grupos', proyecto_id=proyecto.id)
    
    # Obtener los usuarios actuales del grupo
    usuarios_actuales = PerfilProyecto.objects.filter(grupo=grupo).select_related('usuario')
    
    if request.method == 'POST':
        form = AsignarUsuarioGrupoForm(request.POST, proyecto=proyecto, grupo=grupo)
        if form.is_valid():
            perfil = form.save(commit=False)
            perfil.proyecto = proyecto
            perfil.grupo = grupo
            perfil.save()
            grupo.miembros.add(perfil.usuario)
            messages.success(request, f"Usuario '{perfil.usuario.username}' asignado al grupo '{grupo.nombre}'.")
            return redirect('gestionar_grupos', proyecto_id=proyecto.id)
        else:
            messages.error(request, "Error al asignar el usuario. Verifica los datos.")
    else:
        form = AsignarUsuarioGrupoForm(proyecto=proyecto, grupo=grupo)
        form.fields['usuario'].queryset = User.objects.all()
    return render(request, 'core/asignar_usuario_grupo.html', {
        'proyecto': proyecto, 
        'grupo': grupo, 
        'form': form,
        'usuarios_actuales': usuarios_actuales
    })

# Vista para listar notificaciones
@login_required
def lista_notificaciones(request):
    """Muestra las notificaciones del usuario y permite marcarlas como leídas."""
    notificaciones = Notificacion.objects.filter(
        usuario=request.user
    ).select_related('proyecto').order_by('-fecha')
    if request.method == 'POST' and 'marcar_leida' in request.POST:
        notificacion_id = request.POST.get('marcar_leida')
        notificacion = get_object_or_404(Notificacion, id=notificacion_id, usuario=request.user)
        notificacion.leida = True
        notificacion.save()
        messages.success(request, "Notificación marcada como leída.")
        return redirect('lista_notificaciones')
    return render(request, 'core/lista_notificaciones.html', {'notificaciones': notificaciones})

# Vista para eliminar un proyecto
@login_required
def eliminar_proyecto(request, proyecto_id):
    """Elimina un proyecto, restringido a administradores o superusuarios."""
    proyecto = get_object_or_404(
        Proyecto.objects.filter(grupos__miembros=request.user), 
        id=proyecto_id
    )
    es_admin = PerfilProyecto.objects.filter(
        usuario=request.user, proyecto=proyecto, rol='administrador'
    ).exists()
    es_superusuario = request.user.is_superuser
    if not (es_admin or es_superusuario):
        messages.warning(request, "No tienes permiso para eliminar este proyecto.")
        return redirect('lista_proyectos')
    if request.method == 'POST':
        proyecto_titulo = proyecto.titulo
        proyecto.delete()
        messages.success(request, f"El proyecto '{proyecto_titulo}' ha sido eliminado.")
        return redirect('lista_proyectos')
    return render(request, 'core/eliminar_proyecto.html', {'proyecto': proyecto})

# Vista para eliminar una tarea
@login_required
def eliminar_tarea(request, proyecto_id, tarea_id):
    """Elimina una tarea, restringido a administradores o superusuarios."""
    proyecto = get_object_or_404(
        Proyecto.objects.filter(grupos__miembros=request.user), 
        id=proyecto_id
    )
    tarea = get_object_or_404(Tarea, id=tarea_id, proyecto=proyecto)
    es_admin = PerfilProyecto.objects.filter(
        usuario=request.user, proyecto=proyecto, rol='administrador'
    ).exists()
    es_superusuario = request.user.is_superuser
    if not (es_admin or es_superusuario):
        messages.warning(request, "No tienes permiso para eliminar esta tarea.")
        return redirect('lista_tareas', proyecto_id=proyecto.id)
    if request.method == 'POST':
        tarea_titulo = tarea.titulo
        tarea.delete()
        messages.success(request, f"La tarea '{tarea_titulo}' ha sido eliminada.")
        return redirect('lista_tareas', proyecto_id=proyecto.id)
    return render(request, 'core/eliminar_tarea.html', {'proyecto': proyecto, 'tarea': tarea})

# Vista para manejar bloqueos de django-axes
def lockout(request, credentials, *args, **kwargs):
    """Muestra la página de bloqueo cuando se exceden los intentos de login."""
    return render(request, 'core/lockout.html', {'cooloff_time': settings.AXES_COOLOFF_TIME})

# Vista JSON para la bandeja de entrada
@login_required
def bandeja_entrada_json(request):
    """Devuelve datos JSON para la bandeja de entrada del chat y marca notificaciones como leídas."""
    mensajes_recibidos = Mensaje.objects.filter(
        destinatario=request.user
    ).select_related('remitente', 'proyecto').order_by('-fecha_hora')[:5]
    usuarios = User.objects.exclude(id=request.user.id)
    proyectos = Proyecto.objects.filter(grupos__miembros=request.user).distinct()
    
    # Marcar todas las notificaciones no leídas del usuario como leídas al abrir el chat
    Notificacion.objects.filter(
        usuario=request.user,
        leida=False
    ).update(leida=True)
    
    data = {
        'mensajes_recibidos': [
            {
                'id': mensaje.id,
                'remitente': mensaje.remitente.username,
                'proyecto': mensaje.proyecto.titulo if mensaje.proyecto else None,
                'contenido': mensaje.contenido,
                'fecha_hora': mensaje.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')
            } for mensaje in mensajes_recibidos
        ],
        'usuarios': [{'id': usuario.id, 'username': usuario.username} for usuario in usuarios],
        'proyectos': [{'id': proyecto.id, 'titulo': proyecto.titulo} for proyecto in proyectos]
    }
    return JsonResponse(data)

# Vista para la bandeja de entrada completa
@login_required
def bandeja_entrada(request):
    """Muestra la bandeja de entrada completa del usuario."""
    mensajes_recibidos = Mensaje.objects.filter(
        destinatario=request.user
    ).select_related('remitente', 'proyecto').order_by('-fecha_hora')
    mensajes_enviados = Mensaje.objects.filter(
        remitente=request.user
    ).select_related('destinatario', 'proyecto').order_by('-fecha_hora')
    return render(request, 'core/bandeja_entrada.html', {
        'mensajes_recibidos': mensajes_recibidos,
        'mensajes_enviados': mensajes_enviados
    })

# Vista para responder un mensaje
@login_required
def responder_mensaje(request, mensaje_id):
    """Permite responder un mensaje recibido."""
    mensaje_original = get_object_or_404(
        Mensaje, 
        id=mensaje_id, 
        destinatario=request.user
    )
    proyecto = mensaje_original.proyecto
    if request.method == 'POST':
        form = MensajeForm(request.POST, proyecto=proyecto, usuario=request.user)
        if form.is_valid():
            nuevo_mensaje = form.save(commit=False)
            nuevo_mensaje.proyecto = proyecto
            nuevo_mensaje.remitente = request.user
            nuevo_mensaje.destinatario = mensaje_original.remitente
            nuevo_mensaje.save()
            messages.success(request, f"Mensaje enviado a '{nuevo_mensaje.destinatario.username}'.")
            return redirect('bandeja_entrada')
        else:
            messages.error(request, "Error al enviar el mensaje. Verifica los datos.")
    else:
        form = MensajeForm(
            proyecto=proyecto, 
            usuario=request.user, 
            initial={'destinatario': mensaje_original.remitente}
        )
    return render(request, 'core/responder_mensaje.html', {
        'form': form, 
        'proyecto': proyecto, 
        'mensaje_original': mensaje_original
    })

# Vista para enviar mensajes desde el chat modal
@login_required
def enviar_mensaje_chat(request):
    """Envía un mensaje desde el chat modal, con proyecto opcional."""
    if request.method == 'POST':
        form = MensajeForm(request.POST, usuario=request.user)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.remitente = request.user
            mensaje.proyecto = form.cleaned_data.get('proyecto')
            mensaje.save()
            Notificacion.objects.create(
                usuario=mensaje.destinatario,
                mensaje=f"Has recibido un mensaje de {mensaje.remitente}" + 
                        (f" en el proyecto '{mensaje.proyecto.titulo}'" if mensaje.proyecto else ""),
                proyecto=mensaje.proyecto
            )
            return JsonResponse({
                'success': True,
                'contenido': mensaje.contenido,
                'fecha_hora': mensaje.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')
            })
        else:
            return JsonResponse({'success': False, 'error': str(form.errors)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def crear_grupo_general(request):
    """Crea un grupo general que puede asociarse a proyectos posteriormente."""
    if request.method == 'POST':
        form = GrupoForm(request.POST)
        if form.is_valid():
            grupo = form.save(commit=False)
            grupo.save()  # No asignamos proyecto aquí; será opcional
            messages.success(request, f"Grupo '{grupo.nombre}' creado exitosamente.")
            return redirect('lista_proyectos')
        else:
            messages.error(request, "Error al crear el grupo. Verifica el nombre.")
    else:
        form = GrupoForm()
    return render(request, 'core/crear_grupo_general.html', {'form': form})

@login_required
def lista_grupos(request):
    """Muestra todos los grupos a los que pertenece el usuario con sus miembros."""
    grupos = Grupo.objects.filter(miembros=request.user).select_related('proyecto')
    # Obtener los usuarios de cada grupo a través de PerfilProyecto
    for grupo in grupos:
        grupo.usuarios = PerfilProyecto.objects.filter(grupo=grupo).select_related('usuario')
    return render(request, 'core/lista_grupos.html', {'grupos': grupos})