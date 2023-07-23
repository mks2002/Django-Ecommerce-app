from django import template

register = template.Library()


@register.filter(name='multiply')
def multiplyInTemplate(value, arg):
    ans = value*arg
    return ans


# this is our first custom filters of this project this I user for doing multiplication in the template of order page , whenever we have to use it we have to like value | multiply : arg , and for using this we have to import this file in the template by {% load firstcustomFilter  %}