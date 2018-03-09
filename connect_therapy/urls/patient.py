from django.urls import path
from django.views.generic import TemplateView

from connect_therapy.views.patient import *

urlpatterns = [
    path('signup',
         PatientSignUpView.as_view(),
         name="patient-signup"
         ),
    path('signup/success',
         TemplateView.as_view(
             template_name='connect_therapy/patient/signup-success.html'
         ),
         name="patient-signup-success"
         ),
    path('login',
         PatientLoginView.as_view(),
         name='patient-login'
         ),
    path('login/success',
         TemplateView.as_view(
             template_name='connect_therapy/patient/login-success.html'
         ),
         name='patient-login-success'
         ),
    path('logout',
         auth_views.logout,
         {
             'next_page':
                 reverse_lazy('connect_therapy:patient-logout-success'),
         },
         name='patient-logout'
         ),
    path('logout/success',
         TemplateView.as_view(
             template_name='connect_therapy/patient/logout-success.html'
         ),
         name='patient-logout-success'
         ),
    path('my-appointments',
         PatientMyAppointmentsView.as_view(),
         name='patient-my-appointments'
         ),
    path('notes-before-appointment/<int:appointment_id>',
         PatientNotesBeforeView.as_view(),
         name='patient-notes-before'
         ),
    path('',
         TemplateView.as_view(
             template_name='connect_therapy/patient/homepage.html'
         ),
         name='patient-homepage'
         ),
    path('cancel-appointment/<int:pk>',
         PatientCancelAppointmentView.as_view(),
         name='patient-cancel-appointment'
         ),
    path('view-previous-notes/<int:pk>',
         PatientPreviousNotesView.as_view(),
         name='patient-appointment-notes',
         ),
    path('cancel-appointment/<int:pk>',
         PatientCancelAppointmentView.as_view(),
         name='patient-cancel-appointment'
         ),

    path('book-appointment/<int:pk>',
         ViewBookableAppointments.as_view(),
         name='book-appointment'
         ),
    path('book-appointment/<int:pk>/review',
         ReviewSelectedAppointments.as_view(),
         name='book-appointment-review'),
    path('checkout',
         Checkout.as_view(),
         name='checkout'),

    path('profile',
         PatientProfile.as_view(),
         name='patient-profile'
         ),
    path('profile/edit/<int:pk>',
         PatientEditDetailsView.as_view(),
         name='patient-profile-edit'
         ),

]
