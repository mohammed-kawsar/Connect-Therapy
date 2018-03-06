from datetime import date, datetime, time

import pytz
from django.contrib.auth.models import User
from django.test import TestCase

from connect_therapy.models import Practitioner
from connect_therapy.views.patient import *


class PatientNotesBeforeAppointmentTest(TestCase):
    def test_patient_before_notes_form(self):
        u = User(first_name="John", last_name="Smith")
        u.save()
        patient = Patient(user=u,
                          gender='M',
                          mobile="+447476666555",
                          date_of_birth=date(year=1995, month=1, day=1))
        patient.save()
        appointment = Appointment(patient=patient,
                                  start_date_and_time=datetime(year=2018,
                                                               month=4,
                                                               day=17,
                                                               hour=15,
                                                               minute=10,
                                                               tzinfo=pytz.utc),
                                  length=time(hour=1))
        appointment.save()
        patient_before_notes = PatientNotesBeforeView()
        patient_before_notes.appointment = appointment
        form = PatientNotesBeforeForm(data={'patient_notes_before_meeting': 'test'})
        form.is_valid()
        patient_before_notes.form_valid(form)
        self.assertEqual(
            patient_before_notes.appointment.patient_notes_before_meeting, 'test')


class TestPatientCancel(TestCase):
    def test_patient_cancel_form(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12'
                                        )
        user.save()
        practitioner = Practitioner(user=user,
                                    mobile="+44848482732",
                                    bio="ABC",
                                    address_line_1="XXX",
                                    address_line_2="XXXXX",
                                    is_approved=True
                                    )
        practitioner.save()

        user2 = User.objects.create_user(username='test1@example.com',
                                         password='woof12'
                                         )
        user2.save()
        patient = Patient(user=user2,
                          gender='M',
                          mobile="+447476666555",
                          date_of_birth=date(year=1995, month=1, day=1))
        patient.save()
        appointment = Appointment(practitioner=practitioner,
                                  patient=patient,
                                  start_date_and_time=datetime(year=2018,
                                                               month=4,
                                                               day=17,
                                                               hour=15,
                                                               minute=10,
                                                               tzinfo=pytz.utc),
                                  length=time(hour=1))
        appointment.save()
        pcav = PatientCancelAppointmentView()
        pcav.object = appointment
        pcav.form_valid(None)