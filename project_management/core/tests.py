from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Proyecto, Grupo, PerfilProyecto, Tarea, Mensaje, Notificacion
from .forms import ProyectoForm, TareaForm, MensajeForm, AsignarUsuarioGrupoForm
from datetime import date, timedelta

class CoreTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.admin = User.objects.create_superuser(username='admin', password='admin123')
        self.new_user = User.objects.create_user(username='newuser', password='newpass123')  # Nuevo usuario
        self.proyecto = Proyecto.objects.create(
            titulo='Proyecto Test',
            descripcion='Descripción de prueba',
            fecha_inicio=date(2025, 1, 1),
            fecha_fin=date(2025, 2, 1),
            creado_por=self.user
        )
        self.grupo = Grupo.objects.create(nombre='Grupo Test', proyecto=self.proyecto)
        self.perfil = PerfilProyecto.objects.create(
            usuario=self.user,
            proyecto=self.proyecto,
            grupo=self.grupo,
            rol='miembro'
        )
        self.perfil_admin = PerfilProyecto.objects.create(
            usuario=self.admin,
            proyecto=self.proyecto,
            grupo=self.grupo,
            rol='administrador'
        )
        self.grupo.miembros.add(self.user, self.admin)
        self.client.force_login(self.user)

    # Pruebas de Modelos
    def test_proyecto_creation(self):
        self.assertEqual(self.proyecto.titulo, 'Proyecto Test')
        self.assertEqual(self.proyecto.creado_por, self.user)
        self.assertEqual(str(self.proyecto), 'Proyecto Test')

    def test_grupo_creation(self):
        self.assertEqual(self.grupo.nombre, 'Grupo Test')
        self.assertEqual(self.grupo.proyecto, self.proyecto)
        self.assertEqual(str(self.grupo), 'Grupo Test')

    def test_perfil_proyecto_creation(self):
        self.assertEqual(self.perfil.usuario, self.user)
        self.assertEqual(self.perfil.proyecto, self.proyecto)
        self.assertEqual(self.perfil.grupo, self.grupo)
        self.assertEqual(self.perfil.rol, 'miembro')
        self.assertEqual(str(self.perfil), f"{self.user} - miembro en {self.proyecto}")

    def test_tarea_creation(self):
        tarea = Tarea.objects.create(
            proyecto=self.proyecto,
            titulo='Tarea Test',
            descripcion='Descripción tarea',
            fecha_limite=date(2025, 1, 15),
            estado='pendiente'
        )
        tarea.usuarios_asignados.add(self.user)
        self.assertEqual(tarea.titulo, 'Tarea Test')
        self.assertEqual(tarea.proyecto, self.proyecto)
        self.assertIn(self.user, tarea.usuarios_asignados.all())

    def test_mensaje_creation(self):
        mensaje = Mensaje.objects.create(
            remitente=self.user,
            destinatario=self.admin,
            proyecto=self.proyecto,
            contenido='Hola, esto es un mensaje de prueba'
        )
        self.assertEqual(mensaje.remitente, self.user)
        self.assertEqual(mensaje.destinatario, self.admin)
        self.assertEqual(mensaje.contenido, 'Hola, esto es un mensaje de prueba')

    def test_notificacion_creation(self):
        notificacion = Notificacion.objects.create(
            usuario=self.user,
            mensaje='Tarea asignada',
            proyecto=self.proyecto
        )
        self.assertEqual(notificacion.usuario, self.user)
        self.assertEqual(notificacion.mensaje, 'Tarea asignada')
        self.assertFalse(notificacion.leida)

    # Pruebas de Formularios
    def test_proyecto_form_valid(self):
        form_data = {
            'titulo': 'Nuevo Proyecto',
            'descripcion': 'Descripción',
            'fecha_inicio': '2025-01-01',
            'fecha_fin': '2025-02-01',
            'grupos': [self.grupo.id]
        }
        form = ProyectoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_proyecto_form_invalid_dates(self):
        form_data = {
            'titulo': 'Proyecto Inválido',
            'descripcion': 'Descripción',
            'fecha_inicio': '2025-02-01',
            'fecha_fin': '2025-01-01',
            'grupos': [self.grupo.id]
        }
        form = ProyectoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('La fecha de fin no puede ser anterior a la fecha de inicio.', form.errors['__all__'])

    def test_tarea_form_valid(self):
        fecha_futura = date.today() + timedelta(days=7)
        form_data = {
            'titulo': 'Nueva Tarea',
            'descripcion': 'Descripción tarea',
            'fecha_limite': fecha_futura.strftime('%Y-%m-%d'),
            'estado': 'pendiente',
            'usuarios_asignados': [self.user.id]
        }
        form = TareaForm(data=form_data, proyecto=self.proyecto)
        self.assertTrue(form.is_valid(), msg=f"Errores del formulario: {form.errors}")

    def test_mensaje_form_valid(self):
        form_data = {
            'destinatario': str(self.admin.id),
            'proyecto': str(self.proyecto.id),
            'contenido': 'Mensaje de prueba'
        }
        form = MensajeForm(data=form_data, usuario=self.user)
        self.assertTrue(form.is_valid(), msg=f"Errores del formulario: {form.errors}")

    # Pruebas de Vistas
    def test_lista_proyectos_view(self):
        response = self.client.get(reverse('lista_proyectos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/lista_proyectos.html')
        self.assertContains(response, 'Proyecto Test')

    def test_crear_proyecto_view(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('crear_proyecto'), {
            'titulo': 'Proyecto Nuevo',
            'descripcion': 'Descripción nueva',
            'fecha_inicio': '2025-03-01',
            'fecha_fin': '2025-04-01',
            'grupos': [self.grupo.id]
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Proyecto.objects.filter(titulo='Proyecto Nuevo').exists())

    def test_editar_proyecto_view_get(self):
        response = self.client.get(reverse('editar_proyecto', args=[self.proyecto.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/editar_proyecto.html')
        self.assertContains(response, 'Proyecto Test')

    def test_editar_proyecto_view_post(self):
        response = self.client.post(reverse('editar_proyecto', args=[self.proyecto.id]), {
            'titulo': 'Proyecto Editado',
            'descripcion': 'Descripción editada',
            'fecha_inicio': '2025-01-01',
            'fecha_fin': '2025-02-01',
            'grupos': [self.grupo.id]
        })
        self.assertEqual(response.status_code, 302)
        self.proyecto.refresh_from_db()
        self.assertEqual(self.proyecto.titulo, 'Proyecto Editado')

    def test_asignar_usuario_grupo_view(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('asignar_usuario_grupo', args=[self.proyecto.id, self.grupo.id]), {
            'usuario': self.new_user.id,  # Usar un usuario no asignado al grupo
            'rol': 'miembro'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PerfilProyecto.objects.filter(usuario=self.new_user, grupo=self.grupo, rol='miembro').exists())

def es_admin_o_superusuario(user):
    return user.is_superuser or PerfilProyecto.objects.filter(usuario=user, rol='administrador').exists()