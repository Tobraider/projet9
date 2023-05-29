from django import template

register = template.Library()


@register.filter
def model_type(value):
    return type(value).__name__


@register.filter
def ticket_on(value):
    return value.review_set.count()


@register.filter
def make_range(value):
    return range(value)
