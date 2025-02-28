from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_proyectos, name='lista_proyectos'),
    path('proyectos/crear/', views.crear_proyecto, name='crear_proyecto'),
    path('grupos/crear/', views.crear_grupo_general, name='crear_grupo_general'),
    path('grupos/', views.lista_grupos, name='lista_grupos'),
    path('grupos/gestionar/', views.gestionar_grupos, name='gestionar_grupos'),
    path('proyectos/<int:proyecto_id>/editar/', views.editar_proyecto, name='editar_proyecto'),
    path('proyectos/<int:proyecto_id>/tareas/', views.lista_tareas, name='lista_tareas'),
    path('proyectos/<int:proyecto_id>/tareas/crear/', views.crear_tarea, name='crear_tarea'),
    path('proyectos/<int:proyecto_id>/tareas/<int:tarea_id>/editar/', views.editar_tarea, name='editar_tarea'),
    path('proyectos/<int:proyecto_id>/mensajes/', views.mensajes_proyecto, name='mensajes_proyecto'),
    path('proyectos/<int:proyecto_id>/tareas/<int:tarea_id>/comentarios/', views.comentarios_tarea, name='comentarios_tarea'),
    path('proyectos/<int:proyecto_id>/grupos/<int:grupo_id>/asignar/', views.asignar_usuario_grupo, name='asignar_usuario_grupo'),
    path('notificaciones/', views.lista_notificaciones, name='lista_notificaciones'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('proyectos/<int:proyecto_id>/eliminar/', views.eliminar_proyecto, name='eliminar_proyecto'),
    path('proyectos/<int:proyecto_id>/tareas/<int:tarea_id>/eliminar/', views.eliminar_tarea, name='eliminar_tarea'),
    path('lockout/', views.lockout, name='lockout'),
    path('bandeja/json/', views.bandeja_entrada_json, name='bandeja_entrada_json'),
    path('bandeja/', views.bandeja_entrada, name='bandeja_entrada'),
    path('mensajes/responder/<int:mensaje_id>/', views.responder_mensaje, name='responder_mensaje'),
    path('mensajes/enviar/', views.enviar_mensaje_chat, name='enviar_mensaje_chat'),
]