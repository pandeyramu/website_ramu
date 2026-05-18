from django import template

register = template.Library()

@register.filter
def get_option_text(question, option_letter):
    """
    Returns the option text corresponding to 'A', 'B', 'C', 'D'
    """
    mapping = {
        'A': question.option_a,
        'B': question.option_b,
        'C': question.option_c,
        'D': question.option_d,
    }
    return mapping.get(option_letter, '')

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def dict_get(d, key):
    try:
        if d is None:
            return None
        return d.get(str(key), d.get(key))
    except AttributeError:
        return None