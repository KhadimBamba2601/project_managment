from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_proyectos, name='lista_proyectos'),
    path('proyectos/crear/', views.crear_proyecto, name='crear_proyecto'),
    path('proyectos/<int:proyecto_id>/editar/', views.editar_proyecto, name='editar_proyecto'),
    path('proyectos/<int:proyecto_id>/tareas/', views.lista_tareas, name='lista_tareas'),
    path('proyectos/<int:proyecto_id>/tareas/crear/', views.crear_tarea, name='crear_tarea'),
    path('proyectos/<int:proyecto_id>/tareas/<int:tarea_id>/editar/', views.editar_tarea, name='editar_tarea'),
    path('proyectos/<int:proyecto_id>/mensajes/', views.mensajes_proyecto, name='mensajes_proyecto'),
    path('proyectos/<int:proyecto_id>/tareas/<int:tarea_id>/comentarios/', views.comentarios_tarea, name='comentarios_tarea'),
    path('proyectos/<int:proyecto_id>/grupos/', views.gestionar_grupos, name='gestionar_grupos'),
    path('proyectos/<int:proyecto_id>/grupos/<int:grupo_id>/asignar/', views.asignar_usuario_grupo, name='asignar_usuario_grupo'),
]