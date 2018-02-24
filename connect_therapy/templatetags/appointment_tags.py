import humanize
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def string_value(context, appointment):
    first_name = appointment[0].practitioner.user.get_full_name()
    first_date = humanize.naturalday(appointment[0].start_date_and_time)
    first_time = appointment[0].start_date_and_time.time().strftime('%H:%M:%S')
    first_duration = str(appointment[0].length)

    second_name = appointment[1].practitioner.user.get_full_name()
    second_date = humanize.naturalday(appointment[1].start_date_and_time)
    second_time = appointment[1].start_date_and_time.time().strftime('%H:%M:%S')
    second_duration = str(appointment[1].length)

    final_string = first_name + " on " + first_date + " at " + first_time + " for " + first_duration + \
                   " | <== clashes with ==> | " + second_name + " on " + second_date + " at " + second_time + \
                   " for " + second_duration

    return final_string
