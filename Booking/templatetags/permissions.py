from django import template


register = template.Library()

@register.filter(name="has_permission")
def has_permission(user, action_name):
    return user.profile.positions.filter(actions__name=action_name).exists()