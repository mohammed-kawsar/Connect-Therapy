from datetime import date, time

from django.test import TestCase
from django.urls import reverse_lazy

from connect_therapy.models import *


class TestChatView(TestCase):
    def setUp(self):
        test_user_1 = User.objects.create_user(username='testuser1')
        test_user_1.set_password('12345')
        test_user_1.save()

        # test_pat_1 will be assigned to an appointment with test_prac_1
        test_pat_1 = Patient(user=test_user_1,
                             email_confirmed=True,
                             gender='M',
                             mobile="+447476666555",
                             date_of_birth=date(year=1995, month=1, day=1))
        test_pat_1.save()

        test_user_2 = User.objects.create_user(username='testuser2')
        test_user_2.set_password('12345')

        test_user_2.save()

        test_prac_1 = Practitioner(user=test_user_2,
                                   email_confirmed=True,
                                   address_line_1="My home",
                                   postcode="EC12 1CV",
                                   mobile="+447577293232",
                                   bio="Hello")
        test_prac_1.save()

        test_appointment_1 = Appointment(
            practitioner=test_prac_1,
            patient=test_pat_1,
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=15,
                                         minute=16,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        test_appointment_1.save()

        test_appointment_2 = Appointment(
            practitioner=test_prac_1,
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=15,
                                         minute=16,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        test_appointment_2.save()

        test_user_3 = User.objects.create_user(username='testuser3')
        test_user_3.set_password('12345')
        test_user_3.save()

        # test_pat_2 will not be assigned to an appointment
        test_pat_2 = Patient(user=test_user_3,
                             email_confirmed=True,
                             gender='M',
                             mobile="+447476666555",
                             date_of_birth=date(year=1995, month=1, day=1))
        test_pat_2.save()

        test_user_4 = User.objects.create_user(username='testuser4')
        test_user_4.set_password('12345')

        test_user_4.save()
        # will not be assigned to any appointments
        test_prac_2 = Practitioner(user=test_user_4,
                                   email_confirmed=True,
                                   address_line_1="My home",
                                   postcode="EC12 1CV",
                                   mobile="+447577293232",
                                   bio="Hello")
        test_prac_2.save()

    def test_redirect_if_logged_out(self):
        resp = self.client.get(reverse_lazy('connect_therapy:chat', kwargs={'pk': 1}))
        self.assertRedirects(resp, '/patient/login?next=/chat/1')

    def test_redirect_if_wrong_patient(self):
        login = self.client.login(username="testuser3", password="12345")
        resp = self.client.get(reverse_lazy('connect_therapy:chat', kwargs={'pk': 1}))
        self.assertRedirects(resp, '/patient/login?next=/chat/1')

    def test_redirect_if_wrong_practitioner(self):
        login = self.client.login(username="testuser4", password="12345")
        resp = self.client.get(reverse_lazy('connect_therapy:chat', kwargs={'pk': 1}))
        self.assertRedirects(resp, '/patient/login?next=/chat/1')

    def test_correct_template_if_correct_patient(self):
        login = self.client.login(username="testuser1", password="12345")
        resp = self.client.get(reverse_lazy('connect_therapy:chat', kwargs={'pk': 1}))

        # Check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(resp, 'connect_therapy/chat.html')

    def test_correct_template_if_correct_practitioner(self):
        login = self.client.login(username="testuser2", password="12345")
        resp = self.client.get(reverse_lazy('connect_therapy:chat', kwargs={'pk': 1}))

        # Check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser2')
        # Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(resp, 'connect_therapy/chat.html')

    def test_redirect_if_booked_appointment(self):
        login = self.client.login(username="testuser1", password="12345")
        resp = self.client.get(reverse_lazy('connect_therapy:chat', kwargs={'pk': 2}))
        # needs to redirect to the book appointment page for the practitioner of that appointment
        self.assertRedirects(resp, '/patient/book-appointment/1')
