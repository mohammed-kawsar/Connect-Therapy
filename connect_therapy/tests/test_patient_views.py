from datetime import date, datetime

import pytz
from django.test import TestCase

from connect_therapy.views.patient import *


class PatientSignUpTest(TestCase):
    def test_sign_up_redirect(self):
        response = self.client.post('/patient/signup', {
            'first_name': 'Dave',
            'last_name': 'Daverson',
            'gender': 'M',
            'date_of_birth': date(year=1995, month=2, day=20),
            'mobile': '+447075593323',
            'email': 'dave@example.com',
            'password1': 'meowmeow1',
            'password2': 'meowmeow1'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed(response, 'connect_therapy/patient/signup.html')
        self.assertRedirects(response, '/patient/login')


class PatientLoginTest(TestCase):
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

    def test_patient_login_success_redirect(self):
        response = self.client.post('/patient/login', {
            'username': 'testuser1',
            'password': '12345',
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/patient/')

    def test_if_practitioner_cannot_login_on_patients_login(self):
        response = self.client.post('/patient/login', {
            'username': 'testuser3',
            'password': '12345',
        })

        self.assertTemplateUsed(response, 'connect_therapy/patient/login.html')
        self.assertContains(response, 'You are not a patient')

    def test_if_not_a_user_cannot_login(self):
        response = self.client.post('/patient/login', {
            'username': 'testnotuser',
            'password': '12345',
        })

        self.assertTemplateUsed(response, 'connect_therapy/patient/login.html')
        self.assertContains(response, 'Please enter a correct username and '
                                      'password. Note that both fields may be '
                                      'case-sensitive.')


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
                                    mobile="+447476605233",
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
        pcav = PatientCancelAppointmentView()
        pcav.object = appointment
        pcav.form_valid(None)

    def test_split_merged_appointment_into_3(self):
        user = User.objects.create_user('split@yahoo.co.uk',
                                        password='megasword'
                                        )
        user.save()
        patient = Patient(
            user=user,
            gender='M',
            mobile="+447476666555",
            date_of_birth=date(year=1995, month=1, day=1)
        )
        patient.save()
        start_date_and_time = datetime(year=2018,
                                       month=3,
                                       day=11,
                                       hour=12,
                                       minute=00,
                                       tzinfo=pytz.utc)
        appointment = Appointment(patient=patient,
                                  start_date_and_time=start_date_and_time,
                                  length=time(hour=1, minute=30))

        appointment.save()
        p1 = PatientCancelAppointmentView()
        p1.object = appointment
        p1.split_merged_appointment()
        new_appointments = Appointment.objects.filter(
            start_date_and_time__gte=start_date_and_time,
            start_date_and_time__lte=start_date_and_time + timedelta(minutes=60)
        )
        self.assertEqual(len(new_appointments), 3)

        for appointment in new_appointments:
            self.assertEqual(appointment.length, time(minute=30))

            self.assertEquals(appointment.price, Decimal(Appointment._meta.get_field('price').get_default()))

    def test_split_merged_appointment_into_6(self):
        user = User.objects.create_user('split@yahoo.co.uk',
                                        password='megasword'
                                        )
        user.save()
        patient = Patient(
            user=user,
            gender='M',
            mobile="+447476666555",
            date_of_birth=date(year=1995, month=1, day=1)
        )
        patient.save()
        start_date_and_time = datetime(year=2018,
                                       month=3,
                                       day=11,
                                       hour=12,
                                       minute=00,
                                       tzinfo=pytz.utc)
        appointment = Appointment(patient=patient,
                                  start_date_and_time=start_date_and_time,
                                  length=time(hour=3))

        appointment.save()
        p1 = PatientCancelAppointmentView()
        p1.object = appointment
        p1.split_merged_appointment()
        new_appointments = Appointment.objects.filter(
            start_date_and_time__gte=start_date_and_time,
            start_date_and_time__lte=start_date_and_time + timedelta(hours=3)
        )
        self.assertEqual(len(new_appointments), 6)

        for appointment in new_appointments:
            self.assertEqual(appointment.length, time(minute=30))

            self.assertEquals(appointment.price, Decimal(Appointment._meta.get_field('price').get_default()))

    def test_split_merged_appointment_when_no_splits_should_happen(self):
        user = User.objects.create_user('split@yahoo.co.uk',
                                        password='megasword'
                                        )
        user.save()
        patient = Patient(
            user=user,
            gender='M',
            mobile="+447476666555",
            date_of_birth=date(year=1995, month=1, day=1)
        )
        patient.save()
        start_date_and_time = datetime(year=2018,
                                       month=3,
                                       day=11,
                                       hour=12,
                                       minute=00,
                                       tzinfo=pytz.utc)
        appointment = Appointment(patient=patient,
                                  start_date_and_time=start_date_and_time,
                                  length=time(minute=30))
        appointment.save()
        p1 = PatientCancelAppointmentView()
        p1.object = appointment
        p1.split_merged_appointment()
        new_appointments = Appointment.objects.filter(
            start_date_and_time__gte=start_date_and_time,
            start_date_and_time__lte=start_date_and_time + timedelta(minutes=30)
        )
        self.assertEqual(len(new_appointments), 1)
        for appointment in new_appointments:
            self.assertEqual(appointment.length, time(minute=30))


class PatientAppointmentsViewTest(TestCase):
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

    def test_logged_in_patient_view_appointments(self):
        login = self.client.login(username="testuser1", password="12345")
        resp = self.client.get(reverse_lazy('connect_therapy:patient-my-appointments'))

        # Check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(resp, 'connect_therapy/patient/my-appointments.html')

    def test_cannot_view_my_appointments_if_not_logged_in(self):
        resp = self.client.get(reverse_lazy('connect_therapy:patient-my-appointments'))
        # Checks that the response is a redirect.
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/patient/login')

    def test_logged_in_practitioner_cannot_view_patient_appointments(self):
        login = self.client.login(username="testuser3", password="12345")
        resp = self.client.get(reverse_lazy('connect_therapy:patient-my-appointments'))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '/patient/login')


class PatientNotesBeforeTest(TestCase):
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

        appointment = Appointment(
            practitioner=test_prac_1,
            patient=test_pat_1,
            start_date_and_time=datetime(year=timezone.now().year + 1,
                                         month=3,
                                         day=2,
                                         hour=15,
                                         minute=10,
                                         tzinfo=pytz.utc),
            length=time(hour=1),
        )
        appointment.save()

    def test_patient_adding_notes_before_appointment(self):
        login = self.client.login(username="testuser1", password="12345")
        response = self.client.post('/patient/notes-before-appointment/1', {
            'patient_notes_before_meeting': 'Test notes before meeting.',
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/patient/my-appointments')
