from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from connect_therapy.models import *
from connect_therapy.forms import *
from connect_therapy.admin import *
from datetime import date, datetime, time
import pytz
from connect_therapy.views import *


class TestAppointmentOverLap(TestCase):
    "Test the overlap checking algorithm for appointments"

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
        overlaps = Appointment.get_overlaps([a1])
        self.assertEqual(len(overlaps), 0)

    def test_four_same_time(self):
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
                                         day=2,
                                         hour=14,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(hour=3)
        )
        a2.save()

        a3 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=14,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(hour=3)
        )
        a3.save()

        a4 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=14,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(hour=3)
        )
        a4.save()

        overlaps = Appointment.get_overlaps([a1, a2, a3, a4])
        self.assertEquals(len(overlaps), 3)

    def test_two_spread_over_lapping(self):
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
                                         hour=14,
                                         minute=40,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        a2.save()

        overlaps = Appointment.get_overlaps([a1, a2])
        self.assertEquals(len(overlaps), 1)

    def test_four_spread_over_lapping(self):
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
                                         hour=14,
                                         minute=50,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        a2.save()

        a3 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=15,
                                         minute=10,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        a3.save()

        a4 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=16,
                                         minute=00,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        a4.save()

        overlaps = Appointment.get_overlaps([a1, a2, a3, a4])
        self.assertEquals(len(overlaps), 3)

    def test_three_consecutive_one_overlap(self):
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
                                         minute=19,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        a4.save()

        overlaps = Appointment.get_overlaps([a4, a2, a3, a1])
        self.assertEquals(len(overlaps), 1)

    def test_four_disjoint(self):
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
                                         minute=30,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        a2.save()

        a3 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=17,
                                         minute=00,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        a3.save()

        a4 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=18,
                                         minute=10,
                                         tzinfo=pytz.utc),
            length=time(hour=1)
        )
        a4.save()

        overlaps = Appointment.get_overlaps([a4, a2, a3, a1])
        self.assertEquals(len(overlaps), 0)

    def test_slight_over_lap(self):
        a1 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=14,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(minute=1)
        )
        a1.save()

        a2 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=14,
                                         minute=21,
                                         tzinfo=pytz.utc),
            length=time(minute=1)
        )
        a2.save()

        a3 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=14,
                                         minute=22,
                                         tzinfo=pytz.utc),
            length=time(minute=1)
        )
        a3.save()

        a4 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=14,
                                         minute=23,
                                         tzinfo=pytz.utc),
            length=time(minute=1)
        )
        a4.save()

        overlaps = Appointment.get_overlaps([a4, a2, a3, a1])
        self.assertEquals(len(overlaps), 3)

    def test_same_start_different_duartion(self):
        a1 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=14,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(minute=1)
        )
        a1.save()

        a2 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=14,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(minute=2)
        )
        a2.save()

        a3 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=14,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(minute=3)
        )
        a3.save()

        a4 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=14,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=time(minute=4)
        )
        a4.save()

        overlaps = Appointment.get_overlaps([a4, a2, a3, a1])
        self.assertEquals(len(overlaps), 3)
