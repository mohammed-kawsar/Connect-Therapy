from datetime import datetime, time, date

import pytz
from django.contrib.auth.models import User
from django.test import TestCase

from connect_therapy.forms.practitioner import PractitionerNotesForm
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
                                  start_date_and_time=datetime(year=2018,
                                                               month=4,
                                                               day=17,
                                                               hour=15,
                                                               minute=10,
                                                               tzinfo=pytz.utc),
                                  length=time(hour=1))
        appointment.save()
        pnv = PractitionerNotesView()
        pnv.appointment = appointment
        form = PractitionerNotesForm(data={'practitioner_notes': 'test',
                                           'patient_notes_by_practitioner': 'text'})
        form.is_valid()
        pnv.form_valid(form)
        self.assertEqual(pnv.appointment.practitioner_notes, 'test')
        self.assertEqual(pnv.appointment.patient_notes_by_practitioner, 'text')


class TestPractitionerViewPatients(TestCase):
    def test_unique_patient(self):
        john = User(first_name="John", last_name="Smith")
        john.save()
        practitioner = Practitioner(user=john,
                                    address_line_1="My home",
                                    postcode="EC12 1CV",
                                    mobile="+447577293232",
                                    bio="Hello",
                                    is_approved=True)
        practitioner.save()
        robert = User(first_name="Robert", last_name="Greener")
        robert.save()
        patient = Patient(user=robert,
                          gender='M',
                          mobile="+447476666555",
                          date_of_birth=date(year=1995, month=1, day=1))
        patient.save()
        appointment = Appointment(practitioner=practitioner,
                                  start_date_and_time=datetime(year=2018,
                                                               month=4,
                                                               day=17,
                                                               hour=15,
                                                               minute=10,
                                                               tzinfo=pytz.utc),
                                  length=time(hour=1))
        appointment.save()
        appointment = Appointment(practitioner=practitioner,
                                  start_date_and_time=datetime(year=2018,
                                                               month=4,
                                                               day=17,
                                                               hour=15,
                                                               minute=10,
                                                               tzinfo=pytz.utc),
                                  length=time(hour=1))
        appointment.save()
        appointment = Appointment(practitioner=practitioner,
                                  start_date_and_time=datetime(year=2018,
                                                               month=4,
                                                               day=17,
                                                               hour=15,
                                                               minute=10,
                                                               tzinfo=pytz.utc),
                                  length=time(hour=1))
        appointment.save()
