from django.contrib import admin
from .models import Proyecto, Tarea, Mensaje, Comentario, Grupo, PerfilProyecto

admin.site.register(Proyecto)
admin.site.register(Tarea)
admin.site.register(Mensaje)
admin.site.register(Comentario)
admin.site.register(Grupo)
admin.site.register(PerfilProyecto)