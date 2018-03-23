from datetime import date
from urllib.parse import urlencode

from django.test import TestCase
from django.urls import reverse_lazy

from connect_therapy.models import *


class AppointmentBookingViewTest(TestCase):

    def setUp(self):
        # Create two users
        test_user_1 = User.objects.create_user(username='testuser1')
        test_user_1.set_password('12345')
        test_user_1.save()

        test_pat_1 = Patient(user=test_user_1,
                             email_confirmed=True,
                             gender='M',
                             mobile="+447476666555",
                             date_of_birth=date(year=1995, month=1, day=1))
        test_pat_1.save()

        test_user_2 = User.objects.create_user(username='testuser2')
        test_user_2.set_password('12345')
        test_user_2.save()

        test_pat_2 = Patient(user=test_user_2,
                             email_confirmed=True,
                             gender='M',
                             mobile="+447476666555",
                             date_of_birth=date(year=1995, month=1, day=1))
        test_pat_2.save()

        test_user_3 = User.objects.create_user(username='testuser3')
        test_user_3.set_password('12345')

        test_user_3.save()

        test_prac_1 = Practitioner(user=test_user_3,
                                   email_confirmed=True,
                                   address_line_1="My home",
                                   postcode="EC12 1CV",
                                   mobile="+447577293232",
                                   bio="Hello")
        test_prac_1.save()

        test_appointment_1 = Appointment(
            practitioner=test_prac_1,
            start_date_and_time=datetime(year=2018,
                                         month=4,
                                         day=2,
                                         hour=15,
                                         minute=16,
                                         tzinfo=pytz.utc),
            length=timedelta(hours=1)
        )
        test_appointment_1.save()

        test_appointment_2 = Appointment(
            practitioner=test_prac_1,
            start_date_and_time=datetime(year=2018,
                                         month=4,
                                         day=2,
                                         hour=15,
                                         minute=16,
                                         tzinfo=pytz.utc),
            length=timedelta(hours=1)
        )
        test_appointment_2.save()

        test_appointment_3 = Appointment(
            practitioner=test_prac_1,
            start_date_and_time=datetime(year=2018,
                                         month=4,
                                         day=2,
                                         hour=15,
                                         minute=16,
                                         tzinfo=pytz.utc),
            length=timedelta(hours=1)
        )
        test_appointment_3.save()

        test_appointment_4 = Appointment(
            practitioner=test_prac_1,
            start_date_and_time=datetime(year=2018,
                                         month=4,
                                         day=2,
                                         hour=16,
                                         minute=16,
                                         tzinfo=pytz.utc),
            length=timedelta(hours=1)
        )
        test_appointment_4.save()

        test_appointment_5 = Appointment(
            practitioner=test_prac_1,
            start_date_and_time=datetime(year=2018,
                                         month=4,
                                         day=2,
                                         hour=17,
                                         minute=16,
                                         tzinfo=pytz.utc),
            length=timedelta(hours=1)
        )
        test_appointment_5.save()

        test_appointment_6 = Appointment(
            practitioner=test_prac_1,
            start_date_and_time=datetime(year=2018,
                                         month=4,
                                         day=2,
                                         hour=18,
                                         minute=16,
                                         tzinfo=pytz.utc),
            length=timedelta(hours=1)
        )
        test_appointment_6.save()

    def test_redirect_if_not_logged_in_init_booking_page(self):
        resp = self.client.get(reverse_lazy('connect_therapy:patient-book-appointment', kwargs={'pk': 1}))
        self.assertRedirects(resp, '/patient/login?next=/patient/book-appointment/1')

    def test_logged_in_user_correct_template_init_booking_page(self):
        login = self.client.login(username="testuser1", password="12345")
        resp = self.client.get(reverse_lazy('connect_therapy:patient-book-appointment', kwargs={'pk': 1}))

        # Check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(resp, 'connect_therapy/patient/bookings/view-available.html')

    def test_redirect_if_not_logged_in_review_booking_page(self):
        resp = self.client.get(reverse_lazy('connect_therapy:patient-book-appointment-review', kwargs={'pk': 1}))
        self.assertRedirects(resp, '/patient/login?next=/patient/book-appointment/1/review')

    def test_logged_in_user_correct_template_review_booking_page(self):
        login = self.client.login(username="testuser1", password="12345")
        resp = self.client.get(reverse_lazy('connect_therapy:patient-book-appointment-review', kwargs={'pk': 1}))

        # Check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(resp, 'connect_therapy/patient/bookings/review-selection.html')

    def test_redirect_if_not_logged_in_checkout(self):
        resp = self.client.get(reverse_lazy('connect_therapy:patient-checkout'))
        self.assertRedirects(resp, '/patient/login?next=/patient/checkout')

    def test_logged_in_user_correct_template_checkout(self):
        login = self.client.login(username="testuser1", password="12345")
        resp = self.client.get(reverse_lazy('connect_therapy:patient-checkout'))

        # Check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(resp, 'connect_therapy/patient/bookings/checkout.html')

    def test_redirect_if_practitioner_init_booking_page(self):
        login = self.client.login(username="testuser3", password="12345")
        resp = self.client.get(reverse_lazy('connect_therapy:patient-book-appointment', kwargs={'pk': 1}))

        self.assertRedirects(resp, '/patient/login?next=/patient/book-appointment/1')

    def test_redirect_if_practitioner_review_booking_page(self):
        login = self.client.login(username="testuser3", password="12345")
        resp = self.client.get(reverse_lazy('connect_therapy:patient-book-appointment-review', kwargs={'pk': 1}))

        self.assertRedirects(resp, '/patient/login?next=/patient/book-appointment/1/review')

    def test_redirect_if_practitioner_visits_checkout_page(self):
        login = self.client.login(username="testuser3", password="12345")
        resp = self.client.get(reverse_lazy('connect_therapy:patient-checkout'))

        self.assertRedirects(resp, '/patient/login?next=/patient/checkout')

    def test_correct_page_if_user_visits_list_practitioner_page(self):
        login = self.client.login(username="testuser1", password="12345")
        resp = self.client.get(reverse_lazy('connect_therapy:patient-view-practitioners'))

        # Check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(resp, 'connect_therapy/patient/bookings/list-practitioners.html')

    def test_redirect_if_anonymous_visits_list_practitioner_page(self):
        resp = self.client.get(reverse_lazy('connect_therapy:patient-view-practitioners'))
        self.assertRedirects(resp, '/patient/login?next=/patient/view-practitioners')

    def test_redirect_if_practitioner_visits_list_practitioner_page(self):
        login = self.client.login(username="testuser3", password="12345")
        resp = self.client.get(reverse_lazy('connect_therapy:patient-view-practitioners'))
        self.assertRedirects(resp, '/patient/login?next=/patient/view-practitioners')

    def test_view_bookable_appointments_page_post_valid_form(self):
        login = self.client.login(username="testuser1", password="12345")
        resp_get = self.client.get(reverse_lazy('connect_therapy:patient-book-appointment', kwargs={'pk': 1}))

        self.assertEquals(resp_get.status_code, 200)

        data = urlencode({
            'date': datetime.now().date()
        })
        resp_post = self.client.post(reverse_lazy('connect_therapy:patient-book-appointment', kwargs={'pk': 1}), data,
                                     content_type="application/x-www-form-urlencoded")

        self.assertEquals(resp_post.status_code, 200)

    def test_review_bookable_appointments_page_post_with_valid_appointments(self):
        login = self.client.login(username="testuser1", password="12345")
        resp_get = self.client.get(reverse_lazy('connect_therapy:patient-book-appointment-review', kwargs={'pk': 1}))

        self.assertEquals(resp_get.status_code, 200)
        resp_post = self.client.post(reverse_lazy('connect_therapy:patient-book-appointment-review', kwargs={'pk': 1}),
                                     {
                                         'app_id': [4, 5, 6]
                                     })

        self.assertEquals(resp_post.status_code, 200)

    def test_review_bookable_appointments_page_post_with_overlapping_appointments(self):
        login = self.client.login(username="testuser1", password="12345")
        resp_get = self.client.get(reverse_lazy('connect_therapy:patient-book-appointment-review', kwargs={'pk': 1}))

        self.assertEquals(resp_get.status_code, 200)
        resp_post = self.client.post(reverse_lazy('connect_therapy:patient-book-appointment-review', kwargs={'pk': 1}),
                                     {
                                         'app_id': [1, 2, 3]
                                     })

        self.assertEquals(resp_post.status_code, 200)

    def test_review_bookable_appointments_page_post_with_invalid_appointments(self):
        login = self.client.login(username="testuser1", password="12345")
        resp_get = self.client.get(reverse_lazy('connect_therapy:patient-book-appointment-review', kwargs={'pk': 1}))

        self.assertEquals(resp_get.status_code, 200)
        resp_post = self.client.post(reverse_lazy('connect_therapy:patient-book-appointment-review', kwargs={'pk': 1}),
                                     {
                                         'app_id': [12, 13, 14]
                                     })

        self.assertEquals(resp_post.status_code, 200)

    def test_review_bookable_appointments_page_post_with_no_appointments(self):
        login = self.client.login(username="testuser1", password="12345")
        resp_get = self.client.get(reverse_lazy('connect_therapy:patient-book-appointment-review', kwargs={'pk': 1}))

        self.assertEquals(resp_get.status_code, 200)
        resp_post = self.client.post(reverse_lazy('connect_therapy:patient-book-appointment-review', kwargs={'pk': 1}),
                                     {
                                         'app_id': []
                                     })

        self.assertEquals(resp_post.status_code, 302)
        self.assertRedirects(resp_post, reverse_lazy("connect_therapy:patient-book-appointment", kwargs={'pk': 1}))
