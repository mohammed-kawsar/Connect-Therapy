from django.urls import path, reverse_lazy, include, re_path
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

from connect_therapy.views.views import *

app_name = 'connect_therapy'
urlpatterns = [
    path('patient/', include('connect_therapy.urls.patient')),
    path('practitioner/', include('connect_therapy.urls.practitioner')),
    path('chat/<int:pk>',
         ChatView.as_view(),
         name="chat"
         ),
    path('file-upload/<int:pk>',
         FileUploadView.as_view(),
         name='file-upload',
         ),
    path('file-download/<int:pk>',
         FileDownloadView.as_view(),
         name='file-download',
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
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            activate,
            name='activate')
]
