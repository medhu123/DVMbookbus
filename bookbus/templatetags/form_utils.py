from django import template

register = template.Library()

@register.filter
def get_field(form, field_name):
    """Access form fields dynamically"""
    return form[field_name]

@register.filter
def add(value, arg):
    """Concatenate value and arg"""
    return f"{value}{arg}"