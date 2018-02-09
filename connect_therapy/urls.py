from django.urls import path
from django.views.generic import TemplateView

from connect_therapy.views import PatientSignUpView, PatientLoginView

app_name = 'connect_therapy'
urlpatterns = [
    path('patient/signup',
         PatientSignUpView.as_view(),
         name="patient-signup"
         ),
    path('patient/signup/success',
         TemplateView.as_view(
             template_name='connect_therapy/patient/signup-success.html'
         ),
         name="patient-signup-success"
         ),
    path('patient/login',
         PatientLoginView.as_view(),
         name='patient-login'
         ),
    path('patient/login/success',
         TemplateView.as_view(
             template_name='connect_therapy/patient/login-success.html'
         ),
         name='patient-login-success'
         ),
]
