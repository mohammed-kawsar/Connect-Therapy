from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from connect_therapy.models import *
from connect_therapy.forms import *
from connect_therapy.admin import *
from datetime import date, datetime, time
import pytz
from connect_therapy.views import *


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

    def test_session_salt_generation(self):
        u = User(first_name="John", last_name="Smith")
        u.save()
        patient = Patient(user=u,
                          gender='M',
                          mobile="+447476666555",
                          date_of_birth=date(year=1995, month=1, day=1))

        patient.save()

        practitioner = Practitioner(user=u,
                                    address_line_1="My home",
                                    postcode="EC12 1CV",
                                    mobile="+447577293232",
                                    bio="Hello")
        practitioner.save()

        appointment = Appointment(
            practitioner=practitioner,
            patient=patient,
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=15,
                                         minute=16,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        appointment.save()
        self.assertTrue(len(appointment.session_salt) == 10)

    def test_session_id_generation(self):
        u = User(first_name="John", last_name="Smith")
        u.save()
        patient = Patient(user=u,
                          gender='M',
                          mobile="+447476666555",
                          date_of_birth=date(year=1995, month=1, day=1))

        patient.save()

        practitioner = Practitioner(user=u,
                                    address_line_1="My home",
                                    postcode="EC12 1CV",
                                    mobile="+447577293232",
                                    bio="Hello")
        practitioner.save()

        appointment = Appointment(
            practitioner=practitioner,
            patient=patient,
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=15,
                                         minute=16,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        appointment.save()
        self.assertTrue(len(appointment.session_id) > 0)


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


class PractitionerSignUpFormTests(TestCase):
    def test_when_already_exists(self):
        user = User(username="test@example.com", password="woofwoof12")
        user.save()
        form = PractitionerSignUpForm(data={
            'first_name': 'Dave',
            'last_name': 'Daverson',
            'address_line_1': 'M',
            'postcode': 'XXXXX',
            'mobile': '+447075593323',
            'email': 'test@example.com',
            'bio': 'ABC',
            'password1': 'meowmeow1',
            'password2': 'meowmeow1'
        })
        self.assertFalse(form.is_valid())

    def test_when_password_does_not_match(self):
        form = PractitionerSignUpForm(data={
            'first_name': 'Dave',
            'last_name': 'Daverson',
            'address_line_1': 'M',
            'postcode': 'XXXXX',
            'mobile': '+447075593323',
            'email': 'test@example.com',
            'bio': 'ABC',
            'password1': 'meowmeow1',
            'password2': 'meowmeow2'
        })
        self.assertFalse(form.is_valid())

    def test_when_email_is_not_valid(self):
        form = PractitionerSignUpForm(data={
            'first_name': 'Dave',
            'last_name': 'Daverson',
            'address_line_1': 'M',
            'postcode': 'XXXXX',
            'mobile': '+447075593323',
            'email': 'testexample.com',
            'bio': 'ABC',
            'password1': 'meowmeow1',
            'password2': 'meowmeow1'
        })
        self.assertFalse(form.is_valid())

    def test_when_mobile_is_too_long(self):
        form = PractitionerSignUpForm(data={
            'first_name': 'Dave',
            'last_name': 'Daverson',
            'address_line_1': 'M',
            'postcode': 'XXXXX',
            'mobile': '+447075593328282838983233',
            'email': 'test@example.com',
            'bio': 'ABC',
            'password1': 'meowmeow1',
            'password2': 'meowmeow1'
        })
        self.assertFalse(form.is_valid())

    def test_when_valid(self):
        form = PractitionerSignUpForm(data={
            'first_name': 'Dave',
            'last_name': 'Daverson',
            'address_line_1': 'M',
            'postcode': 'XXXXX',
            'mobile': '+447075593323',
            'email': 'test@example.com',
            'bio': 'ABC',
            'password1': 'meowmeow1',
            'password2': 'meowmeow1'
        })
        self.assertTrue(form.is_valid())


class PractitionerLoginFormTests(TestCase):
    def test_when_practitioner_exists_and_valid(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12'
                                        )
        practitioner = Practitioner(user=user,
                                    mobile="+44848482732",
                                    bio="ABC",
                                    address_line_1="XXX",
                                    address_line_2="XXXXX",
                                    is_approved=True
                                    )
        practitioner.save()
        form = PractitionerLoginForm(data={
            'username': 'test@example.com',
            'password': 'woofwoof12'
        })
        self.assertTrue(form.is_valid())

    def test_when_practitioner_exists_and_valid_but_not_approved(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12'
                                        )
        practitioner = Practitioner(user=user,
                                    mobile="+44848482732",
                                    bio="ABC",
                                    address_line_1="XXX",
                                    address_line_2="XXXXX",
                                    is_approved=False
                                    )
        practitioner.save()
        form = PractitionerLoginForm(data={
            'username': 'test@example.com',
            'password': 'woofwoof12'
        })
        self.assertFalse(form.is_valid())

    def test_when_practitioner_does_not_exist(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12'
                                        )
        form = PractitionerLoginForm(data={
            'username': 'test@example.com',
            'password': 'woofwoof12'
        })
        self.assertFalse(form.is_valid())

    def test_when_password_invalid(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12'
                                        )
        practitioner = Practitioner(user=user,
                                    mobile="+44848482732",
                                    bio="ABC",
                                    address_line_1="XXX",
                                    address_line_2="XXXXX",
                                    is_approved=True
                                    )
        practitioner.save()
        form = PatientLoginForm(data={
            'username': 'test@example.com',
            'password': 'woofwoof11'
        })
        self.assertFalse(form.is_valid())

    def test_when_username_invalid(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12'
                                        )
        practitioner = Practitioner(user=user,
                                    mobile="+44848482732",
                                    bio="ABC",
                                    address_line_1="XXX",
                                    address_line_2="XXXXX",
                                    is_approved=True
                                    )
        practitioner.save()
        form = PatientLoginForm(data={
            'username': 'test@demo.com',
            'password': 'woofwoof12'
        })
        self.assertFalse(form.is_valid())


class testPractitionerAdmin(TestCase):
    def test_get_user_first_name(self):
        user = User(first_name="John", last_name="Smith")
        user.save()
        practitioner = Practitioner(user=user,
                                    address_line_1="My home",
                                    postcode="EC12 1CV",
                                    mobile="+447577293232",
                                    bio="Hello")
        self.assertEqual(PractitionerAdmin.get_user_first_name(practitioner),
                         'John'
                         )

    def test_get_user_last_name(self):
        user = User(first_name="John", last_name="Smith")
        user.save()
        practitioner = Practitioner(user=user,
                                    address_line_1="My home",
                                    postcode="EC12 1CV",
                                    mobile="+447577293232",
                                    bio="Hello")
        self.assertEqual(PractitionerAdmin.get_user_last_name(practitioner),
                         'Smith'
                         )

    def test_get_user_email(self):
        user = User(first_name="John",
                    last_name="Smith",
                    email='test@example.com'
                    )
        user.save()
        practitioner = Practitioner(user=user,
                                    address_line_1="My home",
                                    postcode="EC12 1CV",
                                    mobile="+447577293232",
                                    bio="Hello")
        self.assertEqual(PractitionerAdmin.get_user_email(practitioner),
                         'test@example.com')

    def test_mark_approved(self):
        u = User(first_name="John", last_name="Smith")
        u.save()
        practitioner = Practitioner(user=u,
                                    address_line_1="My home",
                                    postcode="EC12 1CV",
                                    mobile="+447577293232",
                                    bio="Hello")
        practitioner.save()
        PractitionerAdmin.mark_approved(None, None, Practitioner.objects.all())
        self.assertEqual(len(Practitioner.objects.filter(is_approved=False)), 0)

        self.assertEqual(len(Practitioner.objects.filter(is_approved=True)), 1)

    def test_not_mark_approved(self):
        u = User(first_name="John", last_name="Smith")
        u.save()
        practitioner = Practitioner(user=u,
                                    address_line_1="My home",
                                    postcode="EC12 1CV",
                                    mobile="+447577293232",
                                    bio="Hello",
                                    is_approved=True)
        practitioner.save()
        PractitionerAdmin.mark_not_approved(None,
                                            None,
                                            Practitioner.objects.all())
        self.assertEqual(len(Practitioner.objects.filter(is_approved=False)),
                         1
                         )
        self.assertEqual(len(Practitioner.objects.filter(is_approved=True)),
                         0
                         )


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

