from datetime import date, datetime, time, timedelta

import pytz
from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase

from connect_therapy.emails import *
from connect_therapy.models import Practitioner, Patient


class EmailTests(TestCase):
    def test_send_password_reset(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12',
                                        first_name="Robert",
                                        last_name="Greener",
                                        email="test@example.com"
                                        )
        user.save()

        send_password_reset(user, "http://example.com")
        self.assertEqual(len(mail.outbox), 1)

    def test_send_patient_appointment_booked(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12',
                                        first_name="Robert",
                                        last_name="Greener",
                                        email="test@example.com"
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
                                         password='woof12',
                                         first_name="Woof",
                                         last_name="Meow",
                                         email="test1@example.com"
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
                                  length=timedelta(hours=1))
        appointment.save()
        send_patient_appointment_booked(appointment)
        self.assertEqual(len(mail.outbox), 1)

    def test_send_patient_reminders(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12',
                                        first_name="Robert",
                                        last_name="Greener",
                                        email="test@example.com"
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
                                         password='woof12',
                                         first_name="Woof",
                                         last_name="Meow",
                                         email="test1@example.com"
                                         )
        user2.save()
        patient = Patient(user=user2,
                          gender='M',
                          mobile="+447476666555",
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

        send_patient_appointment_reminders()
        self.assertEqual(len(mail.outbox), 2)

    def test_send_patient_cancelled_in_good_time(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12',
                                        first_name="Robert",
                                        last_name="Greener",
                                        email="test@example.com"
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
                                         password='woof12',
                                         first_name="Woof",
                                         last_name="Meow",
                                         email="test1@example.com"
                                         )
        user2.save()
        patient = Patient(user=user2,
                          gender='M',
                          mobile="+447476666555",
                          date_of_birth=date(year=1995, month=1, day=1))
        patient.save()
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
        send_patient_cancelled_in_good_time(patient, appointment)
        self.assertEqual(len(mail.outbox), 1)

    def test_send_patient_cancelled_in_under_24_hours(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12',
                                        first_name="Robert",
                                        last_name="Greener",
                                        email="test@example.com"
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
                                         password='woof12',
                                         first_name="Woof",
                                         last_name="Meow",
                                         email="test1@example.com"
                                         )
        user2.save()
        patient = Patient(user=user2,
                          gender='M',
                          mobile="+447476666555",
                          date_of_birth=date(year=1995, month=1, day=1))
        patient.save()
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
        send_patient_cancelled_under_24_hours(patient, appointment)
        self.assertEqual(len(mail.outbox), 1)

    def test_send_patient_confirm_email(self):
        user = User.objects.create_user(username='test1@example.com',
                                        password='woof12',
                                        first_name="Woof",
                                        last_name="Meow",
                                        email="test1@example.com"
                                        )
        user.save()
        patient = Patient(user=user,
                          gender='M',
                          mobile="+447476666555",
                          date_of_birth=date(year=1995, month=1, day=1))
        patient.save()
        send_patient_confirm_email(patient, "http://example.com")
        self.assertEqual(len(mail.outbox), 1)

    def test_send_email_confirmed(self):
        user = User.objects.create_user(username='test1@example.com',
                                        password='woof12',
                                        first_name="Woof",
                                        last_name="Meow",
                                        email="test1@example.com"
                                        )
        user.save()
        patient = Patient(user=user,
                          gender='M',
                          mobile="+447476666555",
                          date_of_birth=date(year=1995, month=1, day=1))
        patient.save()
        send_patient_email_confirmed(patient)
        self.assertEqual(len(mail.outbox), 1)

    def test_send_patient_practitioner_has_cancelled(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12',
                                        first_name="Robert",
                                        last_name="Greener",
                                        email="test@example.com"
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
                                         password='woof12',
                                         first_name="Woof",
                                         last_name="Meow",
                                         email="test1@example.com"
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
                                  length=timedelta(hours=1))
        appointment.save()
        send_patient_practitioner_has_cancelled(appointment)
        send_patient_practitioner_has_cancelled(appointment, "Hello")
        self.assertEqual(len(mail.outbox), 2)

    def test_send_practitioner_appointment_booked(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12',
                                        first_name="Robert",
                                        last_name="Greener",
                                        email="test@example.com"
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
                                         password='woof12',
                                         first_name="Woof",
                                         last_name="Meow",
                                         email="test1@example.com"
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
                                  length=timedelta(hours=1))
        appointment.save()
        send_practitioner_appointment_booked(appointment)
        self.assertEqual(len(mail.outbox), 1)

    def test_send_practitioner_appointment_reminders(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12',
                                        first_name="Robert",
                                        last_name="Greener",
                                        email="test@example.com"
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
                                         password='woof12',
                                         first_name="Woof",
                                         last_name="Meow",
                                         email="test1@example.com"
                                         )
        user2.save()
        patient = Patient(user=user2,
                          gender='M',
                          mobile="+447476666555",
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

        send_practitioner_appointment_reminders()
        self.assertEqual(len(mail.outbox), 2)

    def test_send_practitioner_approved(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12',
                                        first_name="Robert",
                                        last_name="Greener",
                                        email="test@example.com"
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
        send_practitioner_approved(practitioner)
        self.assertEqual(len(mail.outbox), 1)

    def test_send_practitioner_cancelled(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12',
                                        first_name="Robert",
                                        last_name="Greener",
                                        email="test@example.com"
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
        send_practitioner_cancelled(appointment)
        self.assertEqual(len(mail.outbox), 1)

    def test_send_practitioner_confirm_email(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12',
                                        first_name="Robert",
                                        last_name="Greener",
                                        email="test@example.com"
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
        send_practitioner_confirm_email(practitioner, "http://example.com")
        self.assertEqual(len(mail.outbox), 1)

    def test_send_practitioner_email_confirmed(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12',
                                        first_name="Robert",
                                        last_name="Greener",
                                        email="test@example.com"
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
        send_practitioner_email_confirmed(practitioner)
        self.assertEqual(len(mail.outbox), 1)

    def test_send_practitioner_patient_cancelled_in_good_time(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12',
                                        first_name="Robert",
                                        last_name="Greener",
                                        email="test@example.com"
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
                                         password='woof12',
                                         first_name="Woof",
                                         last_name="Meow",
                                         email="test1@example.com"
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
                                  length=timedelta(hours=1))
        appointment.save()
        send_practitioner_patient_cancelled_in_good_time(appointment)
        self.assertEqual(len(mail.outbox), 1)

    def test_send_practitioner_patient_cancelled_in_under_24_hours(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12',
                                        first_name="Robert",
                                        last_name="Greener",
                                        email="test@example.com"
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
                                         password='woof12',
                                         first_name="Woof",
                                         last_name="Meow",
                                         email="test1@example.com"
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
                                  length=timedelta(hours=1))
        appointment.save()
        send_practitioner_patient_cancelled_in_under_24_hours(appointment)
        self.assertEqual(len(mail.outbox), 1)
