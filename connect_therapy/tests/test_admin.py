from django.contrib.auth.models import User
from django.test import TestCase

from connect_therapy.admin import PractitionerAdmin
from connect_therapy.models import Practitioner


class TestPractitionerAdmin(TestCase):
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