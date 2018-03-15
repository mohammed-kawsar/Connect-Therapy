from django import forms


class PasswordResetRequestForm(forms.Form):
    email = forms.CharField(label='email', max_length=250)
