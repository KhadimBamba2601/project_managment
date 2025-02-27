from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Proyecto, Tarea, Mensaje, Comentario, Grupo, PerfilProyecto, Notificacion
from .forms import ProyectoForm, TareaForm, CrearUsuarioForm
import datetime

class ProyectoTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345', email='test@example.com')
        self.admin = User.objects.create_superuser(username='admin', password='admin123', email='admin@example.com')
        self.proyecto = Proyecto.objects.create(
            titulo='Proyecto Test',
            descripcion='Descripción de prueba',
            fecha_inicio='2025-01-01',
            fecha_fin='2025-12-31',
            creado_por=self.user
        )
        self.proyecto.usuarios_asignados.add(self.user)
        PerfilProyecto.objects.create(usuario=self.user, proyecto=self.proyecto, rol='administrador')

    def test_proyecto_creacion(self):
        self.assertEqual(self.proyecto.titulo, 'Proyecto Test')
        self.assertTrue(self.user in self.proyecto.usuarios_asignados.all())

    def test_proyecto_form_validacion_fechas(self):
        form = ProyectoForm(data={
            'titulo': 'Proyecto Inválido',
            'descripcion': 'Test',
            'fecha_inicio': '2025-12-31',
            'fecha_fin': '2025-01-01'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('La fecha de fin no puede ser anterior a la fecha de inicio.', form.errors['__all__'])

class TareaTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.proyecto = Proyecto.objects.create(
            titulo='Proyecto Test',
            descripcion='Descripción',
            fecha_inicio='2025-01-01',
            fecha_fin='2025-12-31',
            creado_por=self.user
        )
        self.proyecto.usuarios_asignados.add(self.user)
        PerfilProyecto.objects.create(usuario=self.user, proyecto=self.proyecto, rol='administrador')
        self.tarea = Tarea.objects.create(
            proyecto=self.proyecto,
            titulo='Tarea Test',
            descripcion='Descripción tarea',
            fecha_limite='2025-06-01',
            estado='pendiente'
        )
        self.tarea.usuarios_asignados.add(self.user)

    def test_tarea_creacion(self):
        self.assertEqual(self.tarea.titulo, 'Tarea Test')
        self.assertEqual(self.tarea.proyecto, self.proyecto)

    def test_tarea_form_validacion_fecha_limite(self):
        form = TareaForm(data={
            'titulo': 'Tarea Inválida',
            'descripcion': 'Descripción válida',
            'fecha_limite': '2020-01-01',
            'estado': 'pendiente'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('fecha_limite', form.errors)

    def test_eliminar_tarea(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('eliminar_tarea', args=[self.proyecto.id, self.tarea.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Tarea.objects.filter(id=self.tarea.id).exists())

class UsuarioTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(username='admin', password='admin123', email='admin@example.com')
        self.proyecto = Proyecto.objects.create(
            titulo='Proyecto Test',
            descripcion='Descripción',
            fecha_inicio='2025-01-01',
            fecha_fin='2025-12-31',
            creado_por=self.admin
        )

    def test_crear_usuario_con_rol(self):
        form_data = {
            'username': 'nuevo_usuario',
            'email': 'nuevo@example.com',
            'password1': 'Test12345',
            'password2': 'Test12345',
            'rol': 'miembro',
            'proyecto': self.proyecto.id
        }
        form = CrearUsuarioForm(data=form_data)
        self.assertTrue(form.is_valid())
        usuario = form.save()
        self.assertEqual(usuario.username, 'nuevo_usuario')
        perfil = PerfilProyecto.objects.get(usuario=usuario)
        self.assertEqual(perfil.rol, 'miembro')
        self.assertEqual(perfil.proyecto, self.proyecto)

    def test_crear_usuario_sin_proyecto(self):
        form_data = {
            'username': 'sin_proyecto',
            'email': 'sinproy@example.com',
            'password1': 'Test12345',
            'password2': 'Test12345',
            'rol': 'miembro',
        }
        form = CrearUsuarioForm(data=form_data)
        self.assertTrue(form.is_valid())
        usuario = form.save()
        self.assertEqual(usuario.username, 'sin_proyecto')
        self.assertFalse(PerfilProyecto.objects.filter(usuario=usuario).exists())

class NotificacionTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.proyecto = Proyecto.objects.create(
            titulo='Proyecto Test',
            descripcion='Descripción',
            fecha_inicio='2025-01-01',
            fecha_fin='2025-12-31',
            creado_por=self.user
        )
        self.proyecto.usuarios_asignados.add(self.user)
        self.notificacion = Notificacion.objects.create(
            usuario=self.user,
            mensaje='Notificación de prueba',
            proyecto=self.proyecto
        )

    def test_marcar_notificacion_leida(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('lista_notificaciones'), {'marcar_leida': self.notificacion.id})
        self.assertEqual(response.status_code, 302)
        self.notificacion.refresh_from_db()
        self.assertTrue(self.notificacion.leida)

class AutenticacionTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.admin = User.objects.create_superuser(username='admin', password='admin123')

    def test_acceso_restringido_no_autenticado(self):
        response = self.client.get(reverse('lista_proyectos'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))

    def test_acceso_admin_crear_usuario(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('crear_usuario'))
        self.assertEqual(response.status_code, 200)

    def test_acceso_no_admin_crear_usuario(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('crear_usuario'))
        self.assertEqual(response.status_code, 302)