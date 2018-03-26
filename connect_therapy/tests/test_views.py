from datetime import date

from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from connect_therapy.models import Practitioner, Patient
from connect_therapy.tokens import account_activation_token
from connect_therapy.views.views import activate


class TestActivate(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_when_uid_not_base_64(self):
        request = self.factory.get('/activate/999/ifsdfkjsd304')
        response = activate(request, 999, 'ifsdfkjsd304')
        self.assertEqual(response.status_code, 302)

    def test_when_uid_not_valid_user(self):
        uidb64 = urlsafe_base64_encode(force_bytes(999))
        request = self.factory.get('/activate/{}/ifsdfkjsd304'.format(uidb64))
        response = activate(request, uidb64, 'ifsdfkjsd304')
        self.assertEqual(response.status_code, 302)

    def test_when_valid_practitioner(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12'
                                        )
        user.save()
        practitioner = Practitioner(user=user,
                                    mobile="+447476605233",
                                    bio="ABC",
                                    address_line_1="XXX",
                                    address_line_2="XXXXX",
                                    is_approved=False
                                    )
        practitioner.save()

        uidb64 = urlsafe_base64_encode(force_bytes(practitioner.user.id))
        token = account_activation_token.make_token(practitioner.user)
        request = self.factory.get('/activate/{0}/{1}'.format(uidb64, token))
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = AnonymousUser()
        response = activate(request, uidb64, token)
        self.assertEqual(request.user, user)
        practitioner.refresh_from_db()
        self.assertTrue(practitioner.email_confirmed)

    def test_when_valid_patient(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12'
                                        )
        user.save()
        patient = Patient(user=user,
                          gender='M',
                          mobile="+447476666555",
                          date_of_birth=date(year=1995, month=1, day=1))
        patient.save()

        uidb64 = urlsafe_base64_encode(force_bytes(patient.user.id))
        token = account_activation_token.make_token(patient.user)
        request = self.factory.get('/activate/{0}/{1}'.format(uidb64, token))
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = AnonymousUser()
        response = activate(request, uidb64, token)
        self.assertEqual(request.user, user)
        patient.refresh_from_db()
        self.assertTrue(patient.email_confirmed)

    def test_when_not_patient_or_practitioner(self):
        user = User.objects.create_user(username='test@example.com',
                                        password='woofwoof12'
                                        )
        user.save()

        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        token = account_activation_token.make_token(user)
        request = self.factory.get('/activate/{0}/{1}'.format(uidb64, token))
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.user = AnonymousUser()
        response = activate(request, uidb64, token)
        self.assertEqual(request.user, user)