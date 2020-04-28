from django import template
from django.contrib.auth.models import Permission

register = template.Library()


@register.filter(takes_context=True)
def user_can_admin(user, group):
    try:
        perm = Permission.objects.get(codename=f"admin_{group}")
    except Permission.DoesNotExist:
        return False
    else:
        if perm in user.user_permissions.all():
            return True
        return False
