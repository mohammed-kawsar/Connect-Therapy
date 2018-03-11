from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase

from connect_therapy.forms.patient import *
from connect_therapy.models import Patient


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
        form = PatientLoginForm(data={
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


class PatientEditProfileTests(TestCase):
    # Test that a patient can successfully update their mobile.
    def test_edit_mobile(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12',
                                        first_name='John',
                                        last_name='Smith'
                                        )
        patient = Patient(user=user,
                          date_of_birth=date(year=1995, month=2, day=20),
                          gender='M',
                          mobile='+447476565333'
                          )
        patient.save()

        patient = PatientForm(instance=user.patient, data={
            'first_name': 'John',
            'last_name': 'Smith',
            'gender': 'M',
            'date_of_birth': date(year=1995, month=2, day=20),
            'email': 'test1@example.com',
            'mobile': '+447075593323',
        })
        patient.save()
        self.assertTrue(patient.is_valid())
        self.assertEqual(str(user.patient.mobile), '+447075593323')

    # Test that a patient can successfully update their email.
    def test_edit_email(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12',
                                        first_name='John',
                                        last_name='Smith'
                                        )
        patient = Patient(user=user,
                          date_of_birth=date(year=1995, month=2, day=20),
                          gender='M',
                          mobile='+447476565333'
                          )
        patient.save()

        patient = PatientUserForm(instance=user, data={
            'first_name': 'John',
            'last_name': 'Smith',
            'gender': 'M',
            'date_of_birth': date(year=1995, month=2, day=20),
            'email': 'test1@example.com',
            'mobile': '+447476565333',
        })
        patient.save()
        self.assertTrue(patient.is_valid())
        self.assertEqual(str(user.email), 'test1@example.com')
