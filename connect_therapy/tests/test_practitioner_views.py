from datetime import datetime, time, date

import pytz
from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase, Client, RequestFactory

from connect_therapy.forms.practitioner.practitioner import PractitionerNotesForm
from connect_therapy.models import Practitioner, Appointment, Patient
from connect_therapy.views.practitioner import *


class PractitionerSignUpTest(TestCase):
    def test_sign_up_redirect(self):
        response = self.client.post((reverse_lazy('connect_therapy:practitioner-signup')), {
            'first_name': 'Chris',
            'last_name': 'Harris',
            'email': 'chris@yahoo.com',
            'mobile': '07893839383',
            'date_of_birth': date(year=1971, month=1, day=1),
            'address_line_1': '1 Fetter Lane',
            'address_line_2': '',
            'postcode': 'E1 WCX',
            'bio': 'Here to serve',
            'password1': 'makapaka!',
            'password2': 'makapaka!'
        })

        response = self.client.get(reverse_lazy('connect_therapy:practitioner-homepage'))

        self.assertEqual(response.status_code, 302)

    def test_form_valid(self):
        response_get = self.client.get(reverse_lazy('connect_therapy:practitioner-signup'))
        self.assertEqual(response_get.status_code, 200)

        data = {
            'first_name': 'Chris',
            'last_name': 'Harris',
            'email': 'chris@yahoo.com',
            'mobile': '07893839383',
            'date_of_birth': date(year=1971, month=1, day=1),
            'address_line_1': '1 Fetter Lane',
            'address_line_2': '',
            'postcode': 'E1 WCX',
            'bio': 'Here to serve',
            'password1': 'makapaka!',
            'password2': 'makapaka!'
        }

        factory = RequestFactory()
        request = factory.post(reverse_lazy('connect_therapy:patient-signup'))
        view = PractitionerSignUpView()
        view.request = request
        form = PractitionerSignUpForm(data=data)
        form.is_valid()
        response = view.form_valid(form)
        try:
            user = User.objects.get(username='chris@yahoo.com')
            self.assertEqual(user.first_name, 'Chris')
        except User.DoesNotExist:
            self.assertTrue(False, 'This should not have been reached')


class PractitionerLoginTest(TestCase):
    def setUp(self):
        test_user_1 = User.objects.create_user(username='testuser1')
        test_user_1.set_password('12345')
        test_user_1.save()

        test_pat_1 = Patient(user=test_user_1,
                             gender='M',
                             mobile="+447476666555",
                             date_of_birth=date(year=1995, month=1, day=1),
                             email_confirmed=True, )
        test_pat_1.save()

        test_user_3 = User.objects.create_user(username='testuser3')
        test_user_3.set_password('12345')

        test_user_3.save()

        test_prac_1 = Practitioner(user=test_user_3,
                                   address_line_1="My home",
                                   postcode="EC12 1CV",
                                   mobile="+447577293232",
                                   bio="Hello",
                                   email_confirmed=True,
                                   is_approved=True)
        test_prac_1.save()

    def test_get_success_url(self):
        view = PractitionerLoginView()
        self.assertEqual(view.get_success_url(), reverse_lazy('connect_therapy:practitioner-homepage'))

    def test_practitioner_login_success_redirect(self):
        login = self.client.login(username="testuser1", password="12345")

        response = self.client.get(reverse_lazy('connect_therapy:practitioner-homepage'))

        self.assertEqual(response.status_code, 302)

    def test_if_practitioner_can_login_on_patients_login(self):
        response = self.client.post('/patient/login', {
            'username': 'testuser3',
            'password': '12345',
        })

        self.assertTemplateUsed(response, 'connect_therapy/patient/login.html')
        self.assertContains(response, 'You are not a patient')

    def test_if_not_a_user_cannot_login(self):
        response = self.client.post('/practitioner/login', {
            'username': 'testnotuser',
            'password': '12345',
        })

        self.assertTemplateUsed(response, 'connect_therapy/practitioner/login.html')
        self.assertContains(response, 'Please enter a correct username and '
                                      'password. Note that both fields may be '
                                      'case-sensitive.')


class TestPractitionerNotes(TestCase):
    def setUp(self):
        test_user_1 = User.objects.create_user(username='testuser1')
        test_user_1.set_password('12345')
        test_user_1.save()
        self.patient = Patient(user=test_user_1,
                          gender='M',
                          mobile="+447476666555",
                          date_of_birth=date(year=1995, month=1, day=1))
        self.patient.save()

        test_user_3 = User.objects.create_user(username='testuser3')
        test_user_3.set_password('12345')

        test_user_3.save()

        self.practitioner = Practitioner(user=test_user_3,
                                         address_line_1="My home",
                                         postcode="EC12 1CV",
                                         mobile="+447577293232",
                                         bio="Hello",
                                         email_confirmed=True,
                                         is_approved=True)
        self.practitioner.save()

        self.appointment = Appointment(patient=self.patient,
                                       practitioner=self.practitioner,
                                  start_date_and_time=datetime.datetime(year=2018,
                                                               month=4,
                                                               day=17,
                                                               hour=15,
                                                               minute=10),
                                  length=timedelta(hours=1))
        self.appointment.save()

    def test_test_func_when_user_has_no_practitioner(self):
        factory = RequestFactory()
        request = factory.post(reverse_lazy('connect_therapy:practitioner-view-notes',
                                            kwargs={'pk': self.appointment.pk}))
        request.user = AnonymousUser()
        view = PractitionerNotesView()
        view.request = request
        self.assertFalse(view.test_func())

    def test_test_func_when_get_object_is_None(self):
        factory = RequestFactory()
        request = factory.post(
            reverse_lazy(
                'connect_therapy:practitioner-view-notes',
                kwargs={'pk': self.appointment.pk}
            )
        )
        request.user = self.practitioner.user
        view = PractitionerNotesView()
        view.request = request
        view.get_object = lambda queryset=None: None
        self.assertFalse(view.test_func())

    def test_test_func_when_different_practitioner(self):
        user = User(username='robert@greener.com', password='meowmeow12')
        user.save()
        practitioner = Practitioner(
            user=user,
            address_line_1='XXX',
            postcode='SG19 2UN',
            bio='XXX',
            is_approved=True,
            email_confirmed=True
        )
        practitioner.save()

        factory = RequestFactory()
        request = factory.post(reverse_lazy('connect_therapy:practitioner-view-notes',
                                            kwargs={'pk': self.appointment.pk}))
        request.user = practitioner.user
        view = PractitionerNotesView()
        view.request = request
        view.get_object = lambda queryset=None: self.appointment
        self.assertFalse(view.test_func())

    def test_test_func_when_email_not_confirmed(self):
        self.practitioner.email_confirmed = False
        self.practitioner.is_approved = True
        self.practitioner.save()

        factory = RequestFactory()
        request = factory.post(reverse_lazy('connect_therapy:practitioner-view-notes',
                                            kwargs={'pk': self.appointment.pk}))
        request.user = self.practitioner.user
        view = PractitionerNotesView()
        view.request = request
        view.get_object = lambda queryset=None: self.appointment
        self.assertFalse(view.test_func())

    def test_test_func_when_not_approved(self):
        self.practitioner.email_confirmed = True
        self.practitioner.is_approved = False
        self.practitioner.save()

        factory = RequestFactory()
        request = factory.post(reverse_lazy('connect_therapy:practitioner-view-notes',
                                            kwargs={'pk': self.appointment.pk}))
        request.user = self.practitioner.user
        view = PractitionerNotesView()
        view.request = request
        view.get_object = lambda queryset=None: self.appointment
        self.assertFalse(view.test_func())

    def test_test_func_when_email_confirmed_and_is_approved(self):
        self.practitioner.email_confirmed = True
        self.practitioner.is_approved = True
        self.practitioner.save()

        factory = RequestFactory()
        request = factory.post(reverse_lazy('connect_therapy:practitioner-view-notes',
                                            kwargs={'pk': self.appointment.pk}))
        request.user = self.practitioner.user
        view = PractitionerNotesView()
        view.request = request
        view.get_object = lambda queryset=None: self.appointment
        self.assertTrue(view.test_func())

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
                                                                        minute=10),
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
                                    email_confirmed=True,
                                    address_line_1="My home",
                                    postcode="EC12 1CV",
                                    mobile="+447577293232",
                                    bio="Hello",
                                    is_approved=True)
        practitioner.save()
        robert = User(username='robert', first_name="Robert", last_name="Greener")
        robert.save()
        patient1 = Patient(user=robert,
                           email_confirmed=True,
                           gender='M',
                           mobile="+447476666555",
                           date_of_birth=date(year=1995, month=1, day=1))
        patient1.save()
        alan = User(username='alan', first_name="Alan", last_name="Brown")
        alan.save()
        patient2 = Patient(user=alan,
                           email_confirmed=True,
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
                                                                         minute=10),
                                   length=timedelta(hours=1))
        appointment1.save()
        appointment2 = Appointment(practitioner=practitioner,
                                   patient=patient2,
                                   start_date_and_time=datetime.datetime(year=2018,
                                                                         month=4,
                                                                         day=17,
                                                                         hour=15,
                                                                         minute=10),
                                   length=timedelta(hours=1))
        appointment2.save()
        appointment3 = Appointment(practitioner=practitioner,
                                   patient=patient2,
                                   start_date_and_time=datetime.datetime(year=2018,
                                                                         month=6,
                                                                         day=14,
                                                                         hour=15,
                                                                         minute=10),
                                   length=timedelta(hours=1))
        appointment3.save()
        c = Client()
        c.force_login(john)
        response = c.get(reverse_lazy('connect_therapy:practitioner-view-patients'))
        self.assertEqual(len(response.context['appointments']), 2)


class PractitionerProfileTest(TestCase):
    def setUp(self):
        test_user_1 = User.objects.create_user(username='testuser1')
        test_user_1.set_password('12345')
        test_user_1.save()

        test_pat_1 = Patient(user=test_user_1,
                             gender='M',
                             mobile="+447476666555",
                             date_of_birth=date(year=1995, month=1, day=1),
                             email_confirmed=True)
        test_pat_1.save()

        test_user_2 = User.objects.create_user(username='testuser3')
        test_user_2.set_password('12345')

        test_user_2.save()

        test_prac_1 = Practitioner(user=test_user_2,
                                   address_line_1="My home",
                                   postcode="EC12 1CV",
                                   mobile="+447577293232",
                                   bio="Hello",
                                   is_approved=True,
                                   email_confirmed=True)
        test_prac_1.save()

    def test_practitioner_can_view_their_profile(self):
        login = self.client.login(username="testuser3", password="12345")
        response = self.client.get(
            reverse_lazy('connect_therapy:practitioner-profile'))

        self.assertEqual(str(response.context['user']), 'testuser3')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'connect_therapy/practitioner/profile.html')

    def test_redirect_patient_cannot_view_practitioner_profile(self):
        login = self.client.login(username="testuser1", password="12345")
        response = self.client.get(
            reverse_lazy('connect_therapy:practitioner-profile'))

        self.assertEqual(response.status_code, 302)

    def test_redirect_practitioner_profile_if_not_logged_in(self):
        response = self.client.get(
            reverse_lazy('connect_therapy:practitioner-profile'))

        self.assertEqual(response.status_code, 302)

    def test_redirect_practitioner_edit_profile(self):
        login = self.client.login(username="testuser2", password="12345")
        response = self.client.post(
            reverse_lazy('connect_therapy:practitioner-profile-edit',
                         kwargs={'pk': 1}), {
                'email': 'chris@yahoo.com',
                'address1': '1 Fetter Lane',
                'address2': 'Waterloo',
                'mobile': '07893839383',
                'date_of_birth': date(year=1971, month=2, day=3),
                'postcode': 'WC2R 2LS',
                'bio': 'Here to serve you',

            })

        response = self.client.get(
            reverse_lazy('connect_therapy:practitioner-profile-edit',
                         kwargs={'pk': 1}))

        self.assertEqual(response.status_code, 302)

    def test_redirect_patient_cannot_view_practitioner_profile_edit(self):
        login = self.client.login(username="testuser1", password="12345")
        response = self.client.get(
            reverse_lazy('connect_therapy:practitioner-profile-edit',
                         kwargs={'pk': 1}))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/practitioner/login')

    def test_redirect_practitioner_edit_if_not_logged_in(self):
        response = self.client.get(
            reverse_lazy('connect_therapy:practitioner-profile-edit',
                         kwargs={'pk': 1}))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/practitioner/login')

    def test_practitioner_change_password(self):
        response = self.client.post(
            reverse_lazy('connect_therapy:practitioner-change-password'), {
                'new_password1': 'password123',
                'new_password2': 'password123',
            })
        self.assertEqual(response.status_code, 302)

    def test_patient_cannot_change_practitioner_password(self):
        login = self.client.login(username="testuser1", password="12345")
        response = self.client.get(
            reverse_lazy('connect_therapy:practitioner-change-password'))

        self.assertEqual(response.status_code, 200)

    def test_if_not_logged_in_cannot_change_practitioner_password(self):
        response = self.client.get(
            reverse_lazy('connect_therapy:practitioner-change-password'))

        self.assertEqual(response.status_code, 302)


class ViewAllPractitionersTest(TestCase):
    def setUp(self):
        test_user_1 = User.objects.create_user(username='testuser1')
        test_user_1.set_password('12345')
        test_user_1.save()

        test_pat_1 = Patient(user=test_user_1,
                             gender='M',
                             mobile="+447476666555",
                             date_of_birth=date(year=1995, month=1, day=1),
                             email_confirmed=True)
        test_pat_1.save()

        test_user_2 = User.objects.create_user(username='testuser3')
        test_user_2.set_password('12345')

        test_user_2.save()

        test_prac_1 = Practitioner(user=test_user_2,
                                   address_line_1="My home",
                                   postcode="EC12 1CV",
                                   mobile="+447577293232",
                                   bio="Hello",
                                   is_approved=True,
                                   email_confirmed=True)
        test_prac_1.save()

    def test_patient_view_all_practitioners(self):
        login = self.client.login(username="testuser1", password="12345")
        response = self.client.get(reverse_lazy(
            'connect_therapy:patient-view-practitioners'))

        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'connect_therapy/patient/bookings/list-practitioners.html')

    def test_practitioner_cannot_view_all_practitioners(self):
        login = self.client.login(username="testuser2", password="12345")
        response = self.client.get(reverse_lazy(
            'connect_therapy:patient-view-practitioners'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
                             '/patient/login?next=/patient/view-practitioners')

    def test_if_not_logged_in_cannot_view_all_practitioners(self):
        response = self.client.get(reverse_lazy(
            'connect_therapy:patient-view-practitioners'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
                             '/patient/login?next=/patient/view-practitioners')


class PractitionerLogoutTest(TestCase):
    def setUp(self):
        test_user_1 = User.objects.create_user(username='testuser1')
        test_user_1.set_password('12345')
        test_user_1.save()

        test_pat_1 = Patient(user=test_user_1,
                             gender='M',
                             mobile="+447476666555",
                             date_of_birth=date(year=1995, month=1, day=1),
                             email_confirmed=True, )
        test_pat_1.save()

        test_user_3 = User.objects.create_user(username='testuser3')
        test_user_3.set_password('12345')

        test_user_3.save()

        test_prac_1 = Practitioner(user=test_user_3,
                                   address_line_1="My home",
                                   postcode="EC12 1CV",
                                   mobile="+447577293232",
                                   bio="Hello",
                                   email_confirmed=True,
                                   is_approved=True)
        test_prac_1.save()

    def test_practitioner_logout_success_redirect(self):
        login = self.client.login(username="testuser2", password="12345")

        logout = self.client.logout()

        response = self.client.get(reverse_lazy('connect_therapy:practitioner-homepage'))

        self.assertEqual(response.status_code, 302)


class PractitionerNotesTest(TestCase):
    def test_sign_up_redirect(self):
        login = self.client.login(username="testuser2", password="12345")
        response = self.client.post(
            reverse_lazy('connect_therapy:practitioner-view-notes',
                         kwargs={'pk': 1}), {
                'text_1': 'Discuss this',
                'text_2': 'Do this',
            })

        response = self.client.get(
            reverse_lazy('connect_therapy:practitioner-view-notes',
                         kwargs={'pk': 1}))

        self.assertEqual(response.status_code, 302)
