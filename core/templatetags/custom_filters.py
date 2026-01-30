from django import template

register = template.Library()

@register.filter
def compact_number(value):
    """
    Formats a number with k/M/B suffixes.
    Example: 1500 -> 1.5k, 1200000 -> 1.2M
    """
    try:
        value = int(value)
    except (ValueError, TypeError):
        return value

    if value < 1000:
        return str(value)
    
    if value < 1000000:
        return f"{value/1000:.1f}k"
    
    if value < 1000000000:
        return f"{value/1000000:.1f}M"
    
    return f"{value/1000000000:.1f}B"

@register.filter(name='eq')
def eq(value, arg):
    """
    Returns True if value is equal to arg.
    Usage: {% if value|eq:arg %}
    """
    return value == arg
