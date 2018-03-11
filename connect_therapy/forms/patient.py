from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import User
from betterforms.multiform import MultiModelForm

from connect_therapy.models import Patient


class PatientSignUpForm(UserCreationForm):
    date_of_birth = forms.DateField(help_text=" Format: DD/MM/YYYY",
                                    input_formats=[
                                        '%d/%m/%Y'
                                    ])
    gender = forms.ChoiceField(choices=Patient.gender_choices)
    mobile = forms.CharField(max_length=20)

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
                  'gender',
                  'date_of_birth',
                  'email',
                  'mobile',
                  'password1',
                  'password2')

        widgets = {
            'email': forms.TextInput(attrs={'size': 35})
        }


class PatientLoginForm(AuthenticationForm):
    username = UsernameField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'autofocus': True,
            'size': 35,
        }, ),
        label="Email"
    )

    def confirm_login_allowed(self, user):
        try:
            user.patient
        except Patient.DoesNotExist:
            raise forms.ValidationError(
                "You are not a patient",
                code='not-patient'
            )
        super().confirm_login_allowed(user)


class PatientNotesBeforeForm(forms.Form):
    patient_notes_before_meeting = forms.CharField(
        label="notes before appointment",
        widget=forms.Textarea
    )



class AppointmentDateSelectForm(forms.Form):
    date = forms.DateField(widget=forms.SelectDateWidget())

    def is_valid(self):
        valid = super(AppointmentDateSelectForm, self).is_valid()
        return valid

class PatientForm(forms.ModelForm):
    date_of_birth = forms.DateField(help_text=" Format: YYYY-MM-DD",
                                    input_formats=[
                                        '%d/%m/%Y', '%Y-%m-%d'
                                    ])
    gender = forms.ChoiceField(choices=Patient.gender_choices)
    mobile = forms.CharField(max_length=20)

    class Meta:
        model = Patient
        fields = ('gender',
                  'date_of_birth',
                  'mobile')

    # Prevents a user from editing these fields in the form.
    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)
        self.fields['gender'].widget.attrs['readonly'] = True
        self.fields['date_of_birth'].widget.attrs['readonly'] = True


class PatientUserForm(forms.ModelForm):
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
        super(PatientUserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['readonly'] = True
        self.fields['last_name'].widget.attrs['readonly'] = True


class PatientEditMultiForm(MultiModelForm):
    form_classes = {
            'user': PatientUserForm,
            'patient': PatientForm
    }
