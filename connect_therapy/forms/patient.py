from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import User

from connect_therapy.models import Patient


class PatientSignUpForm(UserCreationForm):
    date_of_birth = forms.DateField(help_text=" Format: DD/MM/YYYY",
                                    input_formats=[
                                        '%d/%m/%Y'
                                    ])
    gender = forms.ChoiceField(choices=Patient.gender_choices,
                               widget=forms.Select(
                                   attrs={'class': 'form-control',
                                          }))
    mobile = forms.CharField(max_length=20,
                             widget=forms.TextInput(
                                 attrs={'class': 'form-control'}))

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
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'size': 35, 'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.TextInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),

        }

class PatientLoginForm(AuthenticationForm):
    username = UsernameField(
        max_length=254,
        widget=forms.TextInput(
            attrs={'autofocus': True,
                   'size': 35,
                   'class': 'form-control'}, ),
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