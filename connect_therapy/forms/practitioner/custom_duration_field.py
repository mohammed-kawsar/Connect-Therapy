from django import forms


class DurationWidget(forms.MultiWidget):
    def __init__(self, *args, **kwargs):
        CHOICES = kwargs.pop("minute_interval_choices")
        self.widgets = [
            forms.NumberInput(),
            forms.Select(choices=CHOICES)
        ]
        super(DurationWidget, self).__init__(*args, **kwargs, widgets=self.widgets)

    def decompress(self, value):
        if value:
            return decompress_duration(value)
        else:
            return [None,None]


class DurationField(forms.MultiValueField):

    def __init__(self, min_hour_value=0, max_hour_value=2, *args, **kwargs):
        minute_interval_choices = kwargs.pop("minute_interval_choices")
        self.fields = (
            forms.IntegerField(min_value=min_hour_value, max_value=max_hour_value),
            forms.ChoiceField(choices=minute_interval_choices)
        )
        super(DurationField, self).__init__(*args, **kwargs, fields=self.fields)
        self.widget = DurationWidget(minute_interval_choices=minute_interval_choices)

    def compress(self, data_list):
        return compress_duration(data_list)


def decompress_duration(value):
    if value:
        split = value.split('h')
        hour = int(split[0])
        minute_split = split[1].split('m')
        minute = int(minute_split[0])
        return [hour, minute]
    return [None, None]


def compress_duration(data_list):
    if len(data_list) > 0:
        return str(data_list[0]) + "h" + str(data_list[1]) + "m"
    else:
        return ""
