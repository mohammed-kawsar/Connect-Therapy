from datetime import datetime, time, date

import pytz
from django.contrib.auth.models import User
from django.test import TestCase, Client

from connect_therapy.forms.practitioner.practitioner import PractitionerNotesForm
from connect_therapy.models import Practitioner, Appointment, Patient
from connect_therapy.views.practitioner import *


class TestPractitionerNotes(TestCase):
    def test_practitioner_notes_form(self):
        u = User(first_name="John", last_name="Smith")
        u.save()
        practitioner = Practitioner(user=u,
                                    address_line_1="My home",
                                    postcode="EC12 1CV",
                                    mobile="+447577293232",
                                    bio="Hello",
                                    is_approved=True)
        practitioner.save()
        appointment = Appointment(practitioner=practitioner,
                                  start_date_and_time=datetime.datetime(year=2018,
                                                               month=4,
                                                               day=17,
                                                               hour=15,
                                                               minute=10,
                                                               tzinfo=pytz.utc),
                                  length=timedelta(hours=1))
        appointment.save()
        pnv = PractitionerNotesView()
        pnv.object = appointment
        form = PractitionerNotesForm(data={'practitioner_notes': 'test',
                                           'patient_notes_by_practitioner': 'text'})
        form.is_valid()
        pnv.form_valid(form)
        self.assertEqual(pnv.object.practitioner_notes, 'test')
        self.assertEqual(pnv.object.patient_notes_by_practitioner, 'text')


class TestPractitionerAllPatientsView(TestCase):
    def test_unique_patient(self):
        john = User(username='john', first_name="John", last_name="Smith")
        john.save()
        practitioner = Practitioner(user=john,
                                    email_confirmed=True,
                                    address_line_1="My home",
                                    postcode="EC12 1CV",
                                    mobile="+447577293232",
                                    bio="Hello",
                                    is_approved=True)
        practitioner.save()
        robert = User(username='robert', first_name="Robert", last_name="Greener")
        robert.save()
        patient1 = Patient(user=robert,
                           email_confirmed=True,
                           gender='M',
                           mobile="+447476666555",
                           date_of_birth=date(year=1995, month=1, day=1))
        patient1.save()
        alan = User(username='alan', first_name="Alan", last_name="Brown")
        alan.save()
        patient2 = Patient(user=alan,
                           email_confirmed=True,
                           gender='M',
                           mobile="+447477776555",
                           date_of_birth=date(year=1996, month=1, day=1))
        patient2.save()
        appointment1 = Appointment(practitioner=practitioner,
                                   patient=patient1,
                                   start_date_and_time=datetime.datetime(year=2018,
                                                                month=4,
                                                                day=15,
                                                                hour=15,
                                                                minute=10,
                                                                tzinfo=pytz.utc),
                                   length=timedelta(hours=1))
        appointment1.save()
        appointment2 = Appointment(practitioner=practitioner,
                                   patient=patient2,
                                   start_date_and_time=datetime.datetime(year=2018,
                                                                month=4,
                                                                day=17,
                                                                hour=15,
                                                                minute=10,
                                                                tzinfo=pytz.utc),
                                   length=timedelta(hours=1))
        appointment2.save()
        appointment3 = Appointment(practitioner=practitioner,
                                   patient=patient2,
                                   start_date_and_time=datetime.datetime(year=2018,
                                                                month=6,
                                                                day=14,
                                                                hour=15,
                                                                minute=10,
                                                                tzinfo=pytz.utc),
                                   length=timedelta(hours=1))
        appointment3.save()
        c = Client()
        c.force_login(john)
        response = c.get(reverse_lazy('connect_therapy:practitioner-view-patients'))
        self.assertEqual(len(response.context['appointments']), 2)
