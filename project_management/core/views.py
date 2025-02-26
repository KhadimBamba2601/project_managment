from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Proyecto, Tarea, Comentario, Mensaje, PerfilProyecto, Grupo
from .forms import ProyectoForm, TareaForm, MensajeForm, ComentarioForm, GrupoForm, AsignarUsuarioGrupoForm

# Vista para listar proyectos
@login_required
def lista_proyectos(request):
    proyectos = Proyecto.objects.filter(usuarios_asignados=request.user)
    return render(request, 'core/lista_proyectos.html', {'proyectos': proyectos})

# Vista para crear un proyecto (solo administradores, lo ajustaremos después)
@login_required
def crear_proyecto(request):
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proyecto = form.save(commit=False)
            proyecto.creado_por = request.user
            proyecto.save()
            proyecto.usuarios_asignados.add(request.user)  # Añade al creador como asignado
            # Asignar rol de administrador al creador
            PerfilProyecto.objects.create(usuario=request.user, proyecto=proyecto, rol='administrador')
            return redirect('lista_proyectos')
    else:
        form = ProyectoForm()
    return render(request, 'core/crear_proyecto.html', {'form': form})

# Vista para listar tareas de un proyecto
@login_required
def lista_tareas(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id, usuarios_asignados=request.user)
    tareas = Tarea.objects.filter(proyecto=proyecto)
    return render(request, 'core/lista_tareas.html', {'proyecto': proyecto, 'tareas': tareas})

# Vista para crear una tarea
@login_required
def crear_tarea(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id, usuarios_asignados=request.user)
    if request.method == 'POST':
        form = TareaForm(request.POST)
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.proyecto = proyecto
            tarea.save()
            tarea.usuarios_asignados.add(request.user)  # Asigna al creador por defecto
            return redirect('lista_tareas', proyecto_id=proyecto.id)
    else:
        form = TareaForm()
    return render(request, 'core/crear_tarea.html', {'form': form, 'proyecto': proyecto})

# Vista para editar un proyecto (solo administradores)
@login_required
def editar_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id, usuarios_asignados=request.user)
    es_admin = PerfilProyecto.objects.filter(usuario=request.user, proyecto=proyecto, rol='administrador').exists()
    es_creador = proyecto.creado_por == request.user
    es_superusuario = request.user.is_superuser
    if not (es_admin or es_creador or es_superusuario):
        return redirect('lista_proyectos')  # Redirige si no tiene permiso
    if request.method == 'POST':
        form = ProyectoForm(request.POST, instance=proyecto)
        if form.is_valid():
            form.save()
            return redirect('lista_proyectos')
    else:
        form = ProyectoForm(instance=proyecto)
    return render(request, 'core/editar_proyecto.html', {'form': form, 'proyecto': proyecto})

# Vista para editar una tarea (usuarios asignados o administradores)
@login_required
def editar_tarea(request, proyecto_id, tarea_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id, usuarios_asignados=request.user)
    tarea = get_object_or_404(Tarea, id=tarea_id, proyecto=proyecto)
    es_admin = PerfilProyecto.objects.filter(usuario=request.user, proyecto=proyecto, rol='administrador').exists()
    es_asignado = tarea.usuarios_asignados.filter(id=request.user.id).exists()
    es_superusuario = request.user.is_superuser
    if not (es_admin or es_asignado or es_superusuario):
        return redirect('lista_tareas', proyecto_id=proyecto.id)  # Redirige si no tiene permiso
    
    if request.method == 'POST':
        form = TareaForm(request.POST, instance=tarea)
        if form.is_valid():
            form.save()
            return redirect('lista_tareas', proyecto_id=proyecto.id)
    else:
        form = TareaForm(instance=tarea)
    return render(request, 'core/editar_tarea.html', {'form': form, 'proyecto': proyecto, 'tarea': tarea})

# Vista para listar y enviar mensajes en un proyecto
@login_required
def mensajes_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id, usuarios_asignados=request.user)
    mensajes = Mensaje.objects.filter(proyecto=proyecto).order_by('fecha_hora')
    if request.method == 'POST':
        form = MensajeForm(request.POST, proyecto=proyecto, usuario=request.user)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.proyecto = proyecto
            mensaje.remitente = request.user
            mensaje.save()
            return redirect('mensajes_proyecto', proyecto_id=proyecto.id)
    else:
        form = MensajeForm(proyecto=proyecto, usuario=request.user)
    return render(request, 'core/mensajes_proyecto.html', {'proyecto': proyecto, 'mensajes': mensajes, 'form': form})

# Vista para listar y añadir comentarios en una tarea
@login_required
def comentarios_tarea(request, proyecto_id, tarea_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id, usuarios_asignados=request.user)
    tarea = get_object_or_404(Tarea, id=tarea_id, proyecto=proyecto)
    comentarios = Comentario.objects.filter(tarea=tarea).order_by('fecha_hora')
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.tarea = tarea
            comentario.usuario = request.user
            comentario.save()
            return redirect('comentarios_tarea', proyecto_id=proyecto.id, tarea_id=tarea.id)
    else:
        form = ComentarioForm()
    return render(request, 'core/comentarios_tarea.html', {'proyecto': proyecto, 'tarea': tarea, 'comentarios': comentarios, 'form': form})

# Vista para listar y crear grupos en un proyecto
@login_required
def gestionar_grupos(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id, usuarios_asignados=request.user)
    es_admin = PerfilProyecto.objects.filter(usuario=request.user, proyecto=proyecto, rol='administrador').exists()
    es_superusuario = request.user.is_superuser
    if not (es_admin or es_superusuario):
        return redirect('lista_proyectos')
    grupos = Grupo.objects.filter(proyecto=proyecto)
    if request.method == 'POST':
        form = GrupoForm(request.POST)
        if form.is_valid():
            grupo = form.save(commit=False)
            grupo.proyecto = proyecto
            grupo.save()
            return redirect('gestionar_grupos', proyecto_id=proyecto.id)
    else:
        form = GrupoForm()
    return render(request, 'core/gestionar_grupos.html', {'proyecto': proyecto, 'grupos': grupos, 'form': form})

# Vista para asignar usuarios a un grupo
@login_required
def asignar_usuario_grupo(request, proyecto_id, grupo_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id, usuarios_asignados=request.user)
    grupo = get_object_or_404(Grupo, id=grupo_id, proyecto=proyecto)
    es_admin = PerfilProyecto.objects.filter(usuario=request.user, proyecto=proyecto, rol='administrador').exists()
    es_superusuario = request.user.is_superuser
    if not (es_admin or es_superusuario):
        return redirect('gestionar_grupos', proyecto_id=proyecto.id)
    if request.method == 'POST':
        form = AsignarUsuarioGrupoForm(request.POST)
        if form.is_valid():
            perfil = form.save(commit=False)
            perfil.proyecto = proyecto
            perfil.grupo = grupo
            perfil.save()
            grupo.miembros.add(perfil.usuario)
            return redirect('gestionar_grupos', proyecto_id=proyecto.id)
    else:
        form = AsignarUsuarioGrupoForm()
        form.fields['usuario'].queryset = proyecto.usuarios_asignados.all()  # Solo usuarios del proyecto
    return render(request, 'core/asignar_usuario_grupo.html', {'proyecto': proyecto, 'grupo': grupo, 'form': form})