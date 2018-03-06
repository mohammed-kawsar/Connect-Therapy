from django.contrib.auth.models import User
from django.test import TestCase

from connect_therapy.forms.practitioner import *
from connect_therapy.models import Practitioner


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
        form = PractitionerLoginForm(data={
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
        form = PractitionerLoginForm(data={
            'username': 'test@demo.com',
            'password': 'woofwoof12'
        })
        self.assertFalse(form.is_valid())