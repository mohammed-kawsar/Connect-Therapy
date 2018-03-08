from datetime import date, datetime, time

import pytz
from django.contrib.auth.models import User
from django.test import TestCase

from connect_therapy.models import Practitioner, Patient
from connect_therapy.sms import *
from connect_therapy.sms import _send_sms


class TestSMS(TestCase):
    def test__send_sms(self):
        error = False
        try:
            _send_sms("+447476605233", "Hello")
        except Exception:
            error = True

        self.assertEqual(False, error)

    def test_clean_phone_number(self):
        self.assertEqual('+447476605233', clean_phone_number("07476605233"))
        self.assertEqual('+447476605233', clean_phone_number('+447476605233'))
        self.assertEqual('+17476605233', clean_phone_number('0017476605233'))

    def test_send_appointment_booked(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12',
                                        first_name="Robert",
                                        last_name="Greener",
                                        email="test@example.com"
                                        )
        user.save()
        practitioner = Practitioner(user=user,
                                    mobile="+447476605233",
                                    bio="ABC",
                                    address_line_1="XXX",
                                    address_line_2="XXXXX",
                                    is_approved=True
                                    )
        practitioner.save()

        user2 = User.objects.create_user(username='test1@example.com',
                                         password='woof12',
                                         first_name="Woof",
                                         last_name="Meow",
                                         email="test1@example.com"
                                         )
        user2.save()
        patient = Patient(user=user2,
                          gender='M',
                          mobile="+447476605233",
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
        send_appointment_booked(patient, appointment)
        send_appointment_booked(practitioner, appointment)

    def test_send_appointment_cancelled(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12',
                                        first_name="Robert",
                                        last_name="Greener",
                                        email="test@example.com"
                                        )
        user.save()
        practitioner = Practitioner(user=user,
                                    mobile="+447476605233",
                                    bio="ABC",
                                    address_line_1="XXX",
                                    address_line_2="XXXXX",
                                    is_approved=True
                                    )
        practitioner.save()

        user2 = User.objects.create_user(username='test1@example.com',
                                         password='woof12',
                                         first_name="Woof",
                                         last_name="Meow",
                                         email="test1@example.com"
                                         )
        user2.save()
        patient = Patient(user=user2,
                          gender='M',
                          mobile="+447476605233",
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
        send_appointment_cancelled(patient, appointment)
        send_appointment_cancelled(practitioner, appointment)

    def test_send_appointment_reminder(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12',
                                        first_name="Robert",
                                        last_name="Greener",
                                        email="test@example.com"
                                        )
        user.save()
        practitioner = Practitioner(user=user,
                                    mobile="+447476605233",
                                    bio="ABC",
                                    address_line_1="XXX",
                                    address_line_2="XXXXX",
                                    is_approved=True
                                    )
        practitioner.save()

        user2 = User.objects.create_user(username='test1@example.com',
                                         password='woof12',
                                         first_name="Woof",
                                         last_name="Meow",
                                         email="test1@example.com"
                                         )
        user2.save()
        patient = Patient(user=user2,
                          gender='M',
                          mobile="+447476605233",
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
        send_appointment_reminder(patient, appointment)
        send_appointment_reminder(practitioner, appointment)

    def test_send_patient_reminders(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12',
                                        first_name="Robert",
                                        last_name="Greener",
                                        email="test@example.com"
                                        )
        user.save()
        practitioner = Practitioner(user=user,
                                    mobile="+447476605233",
                                    bio="ABC",
                                    address_line_1="XXX",
                                    address_line_2="XXXXX",
                                    is_approved=True
                                    )
        practitioner.save()

        user2 = User.objects.create_user(username='test1@example.com',
                                         password='woof12',
                                         first_name="Woof",
                                         last_name="Meow",
                                         email="test1@example.com"
                                         )
        user2.save()
        patient = Patient(user=user2,
                          gender='M',
                          mobile="+447476605233",
                          date_of_birth=date(year=1995, month=1, day=1))
        patient.save()
        appointment1 = Appointment(practitioner=practitioner,
                                   patient=patient,
                                   start_date_and_time=timezone.now(),
                                   length=time(hour=1))
        appointment1.save()

        appointment2 = Appointment(practitioner=practitioner,
                                   patient=patient,
                                   start_date_and_time=timezone.now(),
                                   length=time(minute=30))
        appointment2.save()

        send_patient_appointment_reminders()

    def test_send_practitioner_reminders(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12',
                                        first_name="Robert",
                                        last_name="Greener",
                                        email="test@example.com"
                                        )
        user.save()
        practitioner = Practitioner(user=user,
                                    mobile="+447476605233",
                                    bio="ABC",
                                    address_line_1="XXX",
                                    address_line_2="XXXXX",
                                    is_approved=True
                                    )
        practitioner.save()

        user2 = User.objects.create_user(username='test1@example.com',
                                         password='woof12',
                                         first_name="Woof",
                                         last_name="Meow",
                                         email="test1@example.com"
                                         )
        user2.save()
        patient = Patient(user=user2,
                          gender='M',
                          mobile="+447476605233",
                          date_of_birth=date(year=1995, month=1, day=1))
        patient.save()
        appointment1 = Appointment(practitioner=practitioner,
                                   patient=patient,
                                   start_date_and_time=timezone.now(),
                                   length=time(hour=1))
        appointment1.save()

        appointment2 = Appointment(practitioner=practitioner,
                                   patient=patient,
                                   start_date_and_time=timezone.now(),
                                   length=time(minute=30))
        appointment2.save()

        send_practitioner_appointment_reminders()