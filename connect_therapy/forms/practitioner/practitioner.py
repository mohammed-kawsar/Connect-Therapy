import datetime

from betterforms.multiform import MultiModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import User

from connect_therapy.forms.practitioner.custom_duration_field import DurationField
from connect_therapy.models import Practitioner


class PractitionerSignUpForm(UserCreationForm):
    address_line_1 = forms.CharField(max_length=100)
    address_line_2 = forms.CharField(max_length=100, required=False)
    postcode = forms.CharField(max_length=10)
    mobile = forms.CharField(max_length=20)
    bio = forms.CharField(widget=forms.Textarea)

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("You've already signed up!",
                                        code='exists'
                                        )
        return email

    class Meta:
        model = User
        fields = ('first_name',
                  'last_name',
                  'email',
                  'mobile',
                  'address_line_1',
                  'address_line_2',
                  'postcode',
                  'bio',
                  'password1',
                  'password2')

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'size': 35, 'class': 'form-control'}),
        }


class PractitionerLoginForm(AuthenticationForm):
    username = UsernameField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True,
                                      'size': 35,
                                      'class': 'form-control'}, ),
        label="Email"
    )

    def confirm_login_allowed(self, user):
        try:
            user.practitioner
        except Practitioner.DoesNotExist:
            raise forms.ValidationError(
                "You are not a practitioner",
                code='not-practitioner'
            )

        if not user.practitioner.is_approved:
            raise forms.ValidationError(
                "You have not been approved",
                code='not-approved'
            )
        super().confirm_login_allowed(user)


class PractitionerNotesForm(forms.Form):
    practitioner_notes = forms.CharField(label="Notes for Practitioner",
                                         widget=forms.Textarea(
                                             attrs={'class': 'form-control'}))
    patient_notes_by_practitioner = forms.CharField(label="Notes for Patient",
                                                    widget=forms.Textarea(
                                                        attrs={'class': 'form-control'}
                                                    ))


class PractitionerForm(forms.ModelForm):
    address_line_1 = forms.CharField(max_length=100)
    address_line_2 = forms.CharField(max_length=100)
    postcode = forms.CharField(max_length=10)
    mobile = forms.CharField(max_length=20)
    bio = forms.Textarea

    class Meta:
        model = Practitioner
        fields = ('address_line_1',
                  'address_line_2',
                  'postcode',
                  'mobile',
                  'bio')

    # Prevents a user from editing these fields in the form.
    def __init__(self, *args, **kwargs):
        super(PractitionerForm, self).__init__(*args, **kwargs)


class PractitionerUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name',
                  'last_name',
                  'email')

        widgets = {
            'email': forms.TextInput(attrs={'size': 35})
        }

    # Prevents a user from editing these fields in the form.
    def __init__(self, *args, **kwargs):
        super(PractitionerUserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['readonly'] = True
        self.fields['last_name'].widget.attrs['readonly'] = True


class PractitionerEditMultiForm(MultiModelForm):
    form_classes = {
        'user': PractitionerUserForm,
        'practitioner': PractitionerForm
    }


class PractitionerDefineAppointmentForm(forms.Form):
    start_date_and_time = forms.DateTimeField(help_text=" Format: DD/MM/YYYY H:M",
                                              required=True,
                                              input_formats=['%d/%m/%Y %H:%M'],
                                              widget=forms.DateInput(attrs={'id': 'datetimepicker',
                                                                            'class': 'form-control'}))
    minute_interval_choices = (
        (00, '00'),
        (30, '30'),
    )
    length = DurationField(required=False, minute_interval_choices=minute_interval_choices)

    def clean_start_date_and_time(self):
        start_datetime = self.cleaned_data['start_date_and_time']

        # Check appointment date is not in past.
        if start_datetime.date() < datetime.date.today():
            raise forms.ValidationError("Invalid date, cannot enter a past date!",
                                        code='invalid'
                                        )
        if start_datetime.date() > datetime.date.today() + datetime.timedelta(weeks=12):
            raise forms.ValidationError("Invalid date, cannot enter a date more than 3 months ahead!",
                                        code='invalid'
                                        )

        return start_datetime
