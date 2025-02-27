from .models import PerfilProyecto, Notificacion

def user_permissions(request):
    is_admin = False
    notificaciones_no_leidas = 0
    if request.user.is_authenticated:
        is_admin = PerfilProyecto.objects.filter(usuario=request.user, rol='administrador').exists()
        notificaciones_no_leidas = Notificacion.objects.filter(usuario=request.user, leida=False).count()
    return {
        'is_admin': is_admin,
        'notificaciones_no_leidas': notificaciones_no_leidas,
    }