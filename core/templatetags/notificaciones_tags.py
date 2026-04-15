from django import template
from core.models import Notificacion

register = template.Library()

@register.simple_tag
def contar_notificaciones_no_leidas(user):
    """Cuenta las notificaciones no leídas de un usuario"""
    if user.is_authenticated:
        return Notificacion.objects.filter(user=user, leida=False).count()
    return 0