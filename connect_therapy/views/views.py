from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView

from connect_therapy.models import Appointment


class ChatView(UserPassesTestMixin, DetailView):
    model = Appointment
    template_name = 'connect_therapy/chat.html'
    login_url = reverse_lazy('connect_therapy:patient-login')

    def get(self, request, *args, **kwargs):
        if self.get_object().patient is None:
            messages.info(request, "You should book an appointment to access this page")
            return redirect(reverse_lazy('connect_therapy:book-appointment',
                                         kwargs={'pk': self.get_object().practitioner.id}))

        return super().get(request, *args, **kwargs)

    def test_func(self):
        # if the patient is empty, we will let the user pass only to redirect them to the book appointment page
        # for this appointment in the get method above
        if self.get_object().patient is None:
            return True
        return (self.request.user.id == self.get_object().patient.user.id) \
               or (self.request.user.id == self.get_object().practitioner.user.id)
