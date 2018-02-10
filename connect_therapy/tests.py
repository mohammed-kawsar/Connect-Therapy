from django.test import TestCase
from django.contrib.auth.models import User
from connect_therapy.models import *
from connect_therapy.forms import *
from datetime import date, datetime, time
import pytz


class PatientModelTests(TestCase):
    def test__str__(self):
        u = User(first_name="John", last_name="Smith")
        u.save()
        patient = Patient(user=u,
                          gender='M',
                          mobile="+447476666555",
                          date_of_birth=date(year=1995, month=1, day=1))
        patient.save()
        self.assertEqual(str(patient), 'John Smith')


class PractitionerModelTests(TestCase):
    def test__str__(self):
        u = User(first_name="John", last_name="Smith")
        u.save()
        practitioner = Practitioner(user=u,
                                    address_line_1="My home",
                                    postcode="EC12 1CV",
                                    mobile="+447577293232",
                                    bio="Hello")
        practitioner.save()
        self.assertEqual(str(practitioner), 'John Smith')


class AppointmentModelTests(TestCase):
    def test__str__(self):
        u = User(first_name="John", last_name="Smith")
        u.save()
        practitioner = Practitioner(user=u,
                                    address_line_1="My home",
                                    postcode="EC12 1CV",
                                    mobile="+447577293232",
                                    bio="Hello")
        practitioner.save()

        appointment = Appointment(
            practitioner=practitioner,
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=15,
                                         minute=16,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        appointment.save()
        self.assertEqual(str(appointment),
                         'John Smith - 2018-03-02 15:16:00+00:00 for 01:00:00')


class PatientSignUpFormTests(TestCase):
    def test_when_already_exists(self):
        user = User(username="test@example.com", password="woofwoof12")
        user.save()
        form = PatientSignUpForm(data={
            'first_name': 'Dave',
            'last_name': 'Daverson',
            'gender': 'M',
            'date_of_birth': date(year=1995, month=2, day=20),
            'mobile': '+447075593323',
            'email': 'test@example.com',
            'password1': 'meowmeow1',
            'password2': 'meowmeow1'
        })
        self.assertFalse(form.is_valid())

    def test_when_password_does_not_match(self):
        form = PatientSignUpForm(data={
            'first_name': 'Dave',
            'last_name': 'Daverson',
            'gender': 'M',
            'date_of_birth': date(year=1995, month=2, day=20),
            'mobile': '+447075593323',
            'email': 'test@example.com',
            'password1': 'meowmeow1',
            'password2': 'meowmeow2'
        })
        self.assertFalse(form.is_valid())

    def test_when_email_is_not_valid(self):
        form = PatientSignUpForm(data={
            'first_name': 'Dave',
            'last_name': 'Daverson',
            'gender': 'M',
            'date_of_birth': date(year=1995, month=2, day=20),
            'mobile': '+447075593323',
            'email': 'testexample.com',
            'password1': 'meowmeow1',
            'password2': 'meowmeow1'
        })
        self.assertFalse(form.is_valid())

    def test_when_mobile_is_too_long(self):
        form = PatientSignUpForm(data={
            'first_name': 'Dave',
            'last_name': 'Daverson',
            'gender': 'M',
            'date_of_birth': date(year=1995, month=2, day=20),
            'mobile': '+447075593323474774848484',
            'email': 'test@example.com',
            'password1': 'meowmeow1',
            'password2': 'meowmeow1'
        })
        self.assertFalse(form.is_valid())

    def test_when_valid(self):
        form = PatientSignUpForm(data={
            'first_name': 'Dave',
            'last_name': 'Daverson',
            'gender': 'M',
            'date_of_birth': date(year=1995, month=2, day=20),
            'mobile': '+447075593323',
            'email': 'test@example.com',
            'password1': 'meowmeow1',
            'password2': 'meowmeow1'
        })
        self.assertTrue(form.is_valid())


class PatientLoginFormTests(TestCase):
    def test_when_patient_exists_and_valid(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12'
                                        )
        patient = Patient(user=user,
                          date_of_birth=date(year=1995, month=2, day=20),
                          gender='M',
                          mobile='+447476565333'
                          )
        patient.save()
        form = PatientLoginForm(data= {
            'username': 'test@example.com',
            'password': 'woofwoof12'
        })
        self.assertTrue(form.is_valid())

    def test_when_patient_does_not_exist(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12'
                                        )
        form = PatientLoginForm(data={
            'username': 'test@example.com',
            'password': 'woofwoof12'
        })
        self.assertFalse(form.is_valid())

    def test_when_password_invalid(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12'
                                        )
        patient = Patient(user=user,
                          date_of_birth=date(year=1995, month=2, day=20),
                          gender='M',
                          mobile='+447476565333'
                          )
        patient.save()
        form = PatientLoginForm(data={
            'username': 'test@example.com',
            'password': 'woofwoof11'
        })
        self.assertFalse(form.is_valid())

    def test_when_username_invalid(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12'
                                        )
        patient = Patient(user=user,
                          date_of_birth=date(year=1995, month=2, day=20),
                          gender='M',
                          mobile='+447476565333'
                          )
        patient.save()
        form = PatientLoginForm(data={
            'username': 'test@demo.com',
            'password': 'woofwoof12'
        })
        self.assertFalse(form.is_valid())

