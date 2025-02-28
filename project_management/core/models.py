from django.db import models
from django.contrib.auth.models import User

class Proyecto(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proyectos_creados')

    def __str__(self):
        return self.titulo

class Grupo(models.Model):
    nombre = models.CharField(max_length=100)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='grupos', null=True, blank=True)
    miembros = models.ManyToManyField(User, through='PerfilProyecto', related_name='grupos')

    def __str__(self):
        return self.nombre

class PerfilProyecto(models.Model):
    ROLES = [
        ('administrador', 'Administrador'),
        ('miembro', 'Miembro'),
        ('invitado', 'Invitado'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    grupo = models.ForeignKey(Grupo, on_delete=models.SET_NULL, null=True, blank=True)
    rol = models.CharField(max_length=20, choices=ROLES, default='miembro')

    def __str__(self):
        return f"{self.usuario} - {self.rol} en {self.proyecto}"

class Tarea(models.Model):
    ESTADO_OPCIONES = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completada', 'Completada'),
    ]
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='tareas')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_limite = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_OPCIONES, default='pendiente')
    usuarios_asignados = models.ManyToManyField(User, related_name='tareas_asignadas')

    def __str__(self):
        return self.titulo

class Mensaje(models.Model):
    remitente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensajes_enviados')
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensajes_recibidos')
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='mensajes', null=True, blank=True)
    contenido = models.TextField()
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Mensaje de {self.remitente} a {self.destinatario}'

class Comentario(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comentario de {self.usuario} en {self.tarea}'

class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Notificación para {self.usuario}: {self.mensaje}"