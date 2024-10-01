from django import template

register = template.Library()

@register.filter
def filter_by_membre(assists, membre):
    return assists.filter(membre=membre).first()