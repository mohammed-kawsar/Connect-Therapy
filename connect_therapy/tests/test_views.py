from datetime import datetime, time, date

import pytz
from django.contrib.auth.models import User
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import AnonymousUser

from connect_therapy.forms.practitioner.practitioner import PractitionerNotesForm
from connect_therapy.views.views import *

from django.contrib.auth.models import User
from django.urls import reverse_lazy

from connect_therapy.models import Patient, Appointment, Practitioner

class TestHelpView(TestCase):
    def test_get_context_data(self):
        factory = RequestFactory()
        request = factory.get(reverse_lazy('connect_therapy/help.html'))
        view = HelpView()
        view.request = request
        view.object = self.appointment
        context = view.get_context_data()
        self.assertEqual(len(context), 'chris@yahoo.com')