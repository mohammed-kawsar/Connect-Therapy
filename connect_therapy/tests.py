from django.test import TestCase
from django.contrib.auth.models import User
from connect_therapy.models import Patient, Practitioner, Appointment
from datetime import date, datetime, time
import pytz


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
