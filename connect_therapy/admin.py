from django.contrib import admin

# Register your models here.
from connect_therapy.models import Appointment, Practitioner, Patient

admin.site.register(Appointment)  # added for testing of video chat feature
admin.site.register(Patient)
admin.site.register(Practitioner)
