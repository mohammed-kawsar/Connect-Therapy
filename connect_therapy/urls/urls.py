from django.urls import path, reverse_lazy, include
from django.views.generic import TemplateView

from connect_therapy.views.views import *

app_name = 'connect_therapy'
urlpatterns = [
    path('patient/', include('connect_therapy.urls.patient')),
    path('practitioner/', include('connect_therapy.urls.practitioner')),
    path('chat/<int:pk>',
         ChatView.as_view(),
         name="chat"
         ),
    path('about',
         TemplateView.as_view(
             template_name='connect_therapy/about.html'
         ),
         name='about'),
    path('',
         TemplateView.as_view(
             template_name='connect_therapy/index.html'
         ),
         name='index'
         ),
]
