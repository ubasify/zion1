from django import template

register = template.Library()

@register.filter
def int_abbrev(value):
    try:
        value = float(value)
    except (ValueError, TypeError):
        return value

    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.1f}k"
    else:
        # returns integer if no decimal part, otherwise float
        return f"{value:.0f}"
