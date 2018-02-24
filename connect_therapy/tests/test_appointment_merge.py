from datetime import datetime, time

import pytz
from django.test import TestCase

from connect_therapy.views import *


class TestAppointmentMerge(TestCase):
    "Test the merging algorithm for appointments"

    def test_one_appointment(self):
        a1 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=14,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(hour=3)
        )
        a1.save()
        merged = Appointment.merge_appointments([a1])
        self.assertEqual(len(merged), 1)

    def test_two_un_mergeable(self):
        a1 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=14,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(hour=3)
        )
        a1.save()

        a2 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=1,
                                         hour=14,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(hour=3)
        )
        a2.save()

        merged = Appointment.merge_appointments([a1, a2])
        self.assertEqual(len(merged), 2)

    def test_two_mergeable(self):
        a1 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=14,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        a1.save()

        a2 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=15,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        a2.save()

        merged = Appointment.merge_appointments([a1, a2])
        self.assertEqual(len(merged), 1)

    def test_two_mergeable_one_not(self):
        a1 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=14,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        a1.save()

        a2 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=15,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        a2.save()

        a3 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=17,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        a3.save()

        merged = Appointment.merge_appointments([a1, a2, a3])
        self.assertEqual(len(merged), 2)

    def test_six_un_mergeable_one_mergeable(self):
        a1 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=14,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        a1.save()

        a2 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=15,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        a2.save()

        a3 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=16,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        a3.save()

        a4 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=17,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        a4.save()

        a5 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=18,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        a5.save()

        a6 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=19,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        a6.save()

        merged = Appointment.merge_appointments([a1, a2, a3, a4, a5, a6])
        self.assertEqual(len(merged), 1)

    def test_six_unmergeable(self):
        a1 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=14,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(minute=30)
        )
        a1.save()

        a2 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=15,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(minute=45)
        )
        a2.save()

        a3 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=16,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(minute=59)
        )
        a3.save()

        a4 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=17,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        a4.save()

        a5 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=18,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(minute=50)
        )
        a5.save()

        a6 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=19,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        a6.save()

        merged = Appointment.merge_appointments([a1, a2, a3, a4, a5, a6])
        print(merged)
        self.assertEqual(len(merged), 5)
