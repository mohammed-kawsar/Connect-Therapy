from django.test import TestCase

from datetime import date, datetime, time

import pytz
from django.contrib.auth.models import User
from django.core import mail

from connect_therapy.models import Patient, Appointment, Practitioner
from connect_therapy.notifications import *


class TestNotifications(TestCase):
    def test_appointment_booked(self):
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
                                  length=timedelta(hours=1))
        appointment.save()
        appointment_booked(appointment)
        self.assertEqual(len(mail.outbox), 2)

    def test_multiple_appointments_booked(self):
        user = User.objects.create_user(username='test44@example.com',
                                        password='woofwoof12',
                                        first_name="Robert",
                                        last_name="Greener",
                                        email="test44@example.com"
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

        user2 = User.objects.create_user(username='test55@example.com',
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
                                  start_date_and_time=datetime(year=2018,
                                                               month=4,
                                                               day=17,
                                                               hour=15,
                                                               minute=10,
                                                               tzinfo=pytz.utc),
                                  length=timedelta(hours=1))
        appointment1.save()
        appointment2 = Appointment(practitioner=practitioner,
                                  patient=patient,
                                  start_date_and_time=datetime(year=2018,
                                                               month=4,
                                                               day=19,
                                                               hour=15,
                                                               minute=10,
                                                               tzinfo=pytz.utc),
                                  length=timedelta(hours=1))
        appointment2.save()
        multiple_appointments_booked((appointment1, appointment2))
        self.assertEqual(len(mail.outbox), 4)

    def test_reminders(self):
        user = User.objects.create_user(username='test1223@example.com',
                                        password='woofwoof12',
                                        first_name="Robert",
                                        last_name="Greener",
                                        email="test1223@example.com"
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

        user2 = User.objects.create_user(username='test1445@example.com',
                                         password='woof12',
                                         first_name="Woof",
                                         last_name="Meow",
                                         email="test1445@example.com"
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
                                   length=timedelta(hours=1))
        appointment1.save()

        appointment2 = Appointment(practitioner=practitioner,
                                   patient=patient,
                                   start_date_and_time=timezone.now(),
                                   length=timedelta(minutes=30))
        appointment2.save()
        reminders()
        self.assertEqual(len(mail.outbox), 4)

    def test_appointment_cancelled_by_patient(self):
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
                                  length=timedelta(hours=1))
        appointment.save()
        appointment_cancelled_by_patient(patient, appointment, False)
        self.assertEqual(len(mail.outbox), 2)
        appointment_cancelled_by_patient(patient, appointment, True)
        self.assertEqual(len(mail.outbox), 4)

    def test_appointment_cancelled_by_practitioner_booked(self):
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
                                  length=timedelta(hours=1))
        appointment.save()
        appointment_cancelled_by_practitioner(appointment)
        self.assertEqual(len(mail.outbox), 2)

    def test_appointment_cancelled_by_practitioner_unbooked(self):
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
        appointment = Appointment(practitioner=practitioner,
                                  patient=None,
                                  start_date_and_time=datetime(year=2018,
                                                               month=4,
                                                               day=17,
                                                               hour=15,
                                                               minute=10,
                                                               tzinfo=pytz.utc),
                                  length=timedelta(hours=1))
        appointment.save()
        appointment_cancelled_by_practitioner(appointment)
        self.assertEqual(len(mail.outbox), 1)
