import json
from datetime import date

from django.test import TestCase

from connect_therapy.models import Patient
from connect_therapy.views.practitioner import *


class TestResendEmailConfirmationView(TestCase):
    def setUp(self):
        # Create two users
        test_user_1 = User.objects.create_user(username='testuser1', email="test1@test.com")
        test_user_1.set_password('12345')
        test_user_1.save()

        test_pat_1 = Patient(user=test_user_1,
                             email_confirmed=True,
                             gender='M',
                             mobile="+447476666555",
                             date_of_birth=date(year=1995, month=1, day=1))
        test_pat_1.save()

        test_user_2 = User.objects.create_user(username='testuser2', email="test2@test.com")
        test_user_2.set_password('12345')
        test_user_2.save()

        test_pat_2 = Patient(user=test_user_2,
                             email_confirmed=False,
                             gender='M',
                             mobile="+447476666555",
                             date_of_birth=date(year=1995, month=1, day=1))
        test_pat_2.save()

        # create 2 test practitioners
        test_user_3 = User.objects.create_user(username='testuser3', email="test3@test.com")
        test_user_3.set_password('12345')

        test_user_3.save()

        test_prac_1 = Practitioner(user=test_user_3,
                                   email_confirmed=True,
                                   address_line_1="My home",
                                   postcode="EC12 1CV",
                                   mobile="+447577293232",
                                   bio="Hello")
        test_prac_1.save()

        test_user_4 = User.objects.create_user(username='testuser4', email="test4@test.com")
        test_user_4.set_password('12345')

        test_user_4.save()

        test_prac_2 = Practitioner(user=test_user_4,
                                   email_confirmed=False,
                                   address_line_1="My home",
                                   postcode="EC12 1CV",
                                   mobile="+447577293232",
                                   bio="Hello")
        test_prac_2.save()

    def test_valid_email_active_account_send_confirmation_patient(self):
        resp = self.client.post(reverse_lazy('connect_therapy:send-email-confirmation'), {
            'email_address': 'test1@test.com'
        })
        content = json.loads(resp.content)
        valid_format = content["validEmailFormat"]
        sent = content['sent']
        # the email for this user (user 1) has already been activated above, so email won't have been sent
        self.assertTrue(valid_format)
        self.assertFalse(sent)

    def test_valid_email_active_account_send_confirmation_practitioner(self):
        resp = self.client.post(reverse_lazy('connect_therapy:send-email-confirmation'), {
            'email_address': 'test3@test.com'
        })
        content = json.loads(resp.content)
        valid_format = content["validEmailFormat"]
        sent = content['sent']
        # the email for this user (user 3) has already been activated above, so email won't have been sent
        self.assertTrue(valid_format)
        self.assertFalse(sent)

    def test_valid_email_inactive_account_send_confirmation_patient(self):
        resp = self.client.post(reverse_lazy('connect_therapy:send-email-confirmation'), {
            'email_address': 'test2@test.com'
        })
        content = json.loads(resp.content)
        valid_format = content["validEmailFormat"]
        sent = content['sent']
        self.assertTrue(valid_format)
        self.assertTrue(sent)

    def test_valid_email_inactive_account_send_confirmation_practitioner(self):
        resp = self.client.post(reverse_lazy('connect_therapy:send-email-confirmation'), {
            'email_address': 'test4@test.com'
        })
        content = json.loads(resp.content)
        valid_format = content["validEmailFormat"]
        sent = content['sent']
        self.assertTrue(valid_format)
        self.assertTrue(sent)

    def test_invalid_email_one(self):
        resp = self.client.post(reverse_lazy('connect_therapy:send-email-confirmation'), {
            'email_address': 'test2test.com'
        })
        content = json.loads(resp.content)
        valid_format = content["validEmailFormat"]
        sent = content['sent']
        self.assertFalse(valid_format)
        self.assertFalse(sent)

    def test_invalid_email_two(self):
        resp = self.client.post(reverse_lazy('connect_therapy:send-email-confirmation'), {
            'email_address': '"'
        })
        content = json.loads(resp.content)
        valid_format = content["validEmailFormat"]
        sent = content['sent']
        self.assertFalse(valid_format)
        self.assertFalse(sent)

    def test_invalid_email_three(self):
        resp = self.client.post(reverse_lazy('connect_therapy:send-email-confirmation'), {
            'email_address': '4903390580943095@84309'
        })
        content = json.loads(resp.content)
        valid_format = content["validEmailFormat"]
        sent = content['sent']
        self.assertFalse(valid_format)
        self.assertFalse(sent)

    def test_invalid_email_four(self):
        resp = self.client.post(reverse_lazy('connect_therapy:send-email-confirmation'), {
            'email_address': '@SDFSDSDSFDDSF'
        })
        content = json.loads(resp.content)
        valid_format = content["validEmailFormat"]
        sent = content['sent']
        self.assertFalse(valid_format)
        self.assertFalse(sent)
