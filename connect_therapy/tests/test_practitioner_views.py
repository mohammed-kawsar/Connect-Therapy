from datetime import datetime, time, date

import pytz
from django.contrib.auth.models import User
from django.test import TestCase, Client

from connect_therapy.forms.practitioner.practitioner import PractitionerNotesForm
from connect_therapy.models import Practitioner, Appointment, Patient
from connect_therapy.views.practitioner import *


class PractitionerSignUpTest(TestCase):
    def test_sign_up_redirect(self):
        response = self.client.post('/practitioner/signup', {
            'first_name': 'Chris',
            'last_name': 'Harris',
            'email': 'chris@yahoo.com',
            'mobile': '07893839383',
            'date_of_birth': date(year=1971, month=1, day=1),
            'address1': '1 Fetter Lane',
            'address2': '',
            'postcode': 'E1 WCX',
            'bio': 'Here to serve',
            'password1': 'makapaka!',
            'password2': 'makapaka!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse_lazy('app:signup'), fetch_redirect_response=False)
        self.assertTemplateUsed(response, 'connect_therapy/practitioner/signup.html')
        self.assertRedirects(response, '/practitioner/login', status_code=302,
                             target_status_code=302)


class PractitionerLoginTest(TestCase):
    def setUp(self):
        test_user_1 = User.objects.create_user(username='testuser1')
        test_user_1.set_password('12345')
        test_user_1.save()

        test_pat_1 = Patient(user=test_user_1,
                             gender='M',
                             mobile="+447476666555",
                             date_of_birth=date(year=1995, month=1, day=1))
        test_pat_1.save()

        test_user_3 = User.objects.create_user(username='testuser3')
        test_user_3.set_password('12345')

        test_user_3.save()

        test_prac_1 = Practitioner(user=test_user_3,
                                   address_line_1="My home",
                                   postcode="EC12 1CV",
                                   mobile="+447577293232",
                                   bio="Hello")
        test_prac_1.save()

    def test_practitioner_login_success_redirect(self):
        response = self.client.post('/practitioner/login', {
            'username': 'testuser1',
            'password': '12345',
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse_lazy('app:login'), fetch_redirect_response=False)
        self.assertRedirects(response, '/practitioner/', status_code=302,
                             target_status_code=302)

    def test_if_practitioner_can_login_on_patients_login(self):
        response = self.client.post('/patient/login', {
            'username': 'testuser3',
            'password': '12345',
        })

        self.assertTemplateUsed(response, 'connect_therapy/patient/login.html')
        self.assertContains(response, 'You are not a patient')


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
                                    address_line_1="My home",
                                    postcode="EC12 1CV",
                                    mobile="+447577293232",
                                    bio="Hello",
                                    is_approved=True)
        practitioner.save()
        robert = User(username='robert', first_name="Robert", last_name="Greener")
        robert.save()
        patient1 = Patient(user=robert,
                           gender='M',
                           mobile="+447476666555",
                           date_of_birth=date(year=1995, month=1, day=1))
        patient1.save()
        alan = User(username='alan', first_name="Alan", last_name="Brown")
        alan.save()
        patient2 = Patient(user=alan,
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
