from django import forms

from connect_therapy.models import File


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ('file_name', 'file')