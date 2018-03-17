from datetime import datetime, time, timedelta
from decimal import Decimal

import pytz
from django.test import TestCase

from connect_therapy.models import Appointment


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
            length=timedelta(hours=3)
        )
        a1.save()
        merged, unmerged = Appointment.merge_appointments([a1])
        self.assertEqual(len(merged), 1)

    def test_two_un_mergeable(self):
        a1 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=14,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=timedelta(hours=3)
        )
        a1.save()

        a2 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=1,
                                         hour=14,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=timedelta(hours=3)
        )
        a2.save()

        merged, unmerged = Appointment.merge_appointments([a1, a2])
        self.assertEqual(len(merged), 2)

    def test_two_mergeable(self):
        a1 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=19,
                                         hour=18,
                                         minute=10,
                                         tzinfo=pytz.utc),
            length=timedelta(minutes=30),
            price=Decimal(50.00)
        )
        a1.save()

        a2 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=19,
                                         hour=18,
                                         minute=40,
                                         tzinfo=pytz.utc),

            length=timedelta(minutes=30),
            price=Decimal(50.00)

        )
        a2.save()

        merged, unmerged = Appointment.merge_appointments([a1, a2])
        self.assertEqual(len(merged), 1)
        self.assertEquals(merged[0].price, Decimal(100.00))

    def test_two_mergeable_one_not(self):
        a1 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=14,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=timedelta(hours=1),
            price=Decimal(50.00)
        )
        a1.save()

        a2 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=15,
                                         minute=20,
                                         tzinfo=pytz.utc),

            length=timedelta(hours=1),
            price=Decimal(50.00)

        )
        a2.save()

        a3 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=17,
                                         minute=20,
                                         tzinfo=pytz.utc),

            length=timedelta(hours=1),
            price=Decimal(50.00)

        )
        a3.save()

        merged, unmerged = Appointment.merge_appointments([a1, a2, a3])
        self.assertEqual(len(merged), 2)
        self.assertEquals(merged[0].price, Decimal(100.00))

    def test_six_mergeable(self):
        a1 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=14,
                                         minute=20,
                                         tzinfo=pytz.utc),

            length=timedelta(hours=1),
            price=Decimal(50.00)
        )
        a1.save()

        a2 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=15,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=timedelta(hours=1),
            price=Decimal(50.00)

        )
        a2.save()

        a3 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=16,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=timedelta(hours=1),
            price=Decimal(50.00)
        )
        a3.save()

        a4 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=17,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=timedelta(hours=1),
            price=Decimal(50.00)
        )
        a4.save()

        a5 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=18,
                                         minute=20,
                                         tzinfo=pytz.utc),

            length=timedelta(hours=1),
            price=Decimal(50.00)
        )
        a5.save()

        a6 = Appointment(

            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=19,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=timedelta(hours=1),
            price=Decimal(50.00)
        )
        a6.save()

        merged, unmerged = Appointment.merge_appointments([a1, a2, a3, a4, a5, a6])
        self.assertEqual(len(merged), 1)
        self.assertEquals(merged[0].price, 300)

    def test_five_unmergeable_one_mergeable(self):
        a1 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=14,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=timedelta(minutes=30),
            price=Decimal(50.00)
        )
        a1.save()

        a2 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=15,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=timedelta(minutes=45),
            price=Decimal(50.00)

        )
        a2.save()

        a3 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=16,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=timedelta(minutes=59),
            price=Decimal(50.00)
        )
        a3.save()

        a4 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=17,
                                         minute=20,
                                         tzinfo=pytz.utc),

            length=timedelta(hours=1),
            price=Decimal(50.00)
        )
        a4.save()

        a5 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=18,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=timedelta(minutes=50),
            price=Decimal(50.00)
        )
        a5.save()

        a6 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=19,
                                         minute=20,
                                         tzinfo=pytz.utc),

            length=timedelta(hours=1),
            price=Decimal(50.00)

        )
        a6.save()

        merged, unmerged = Appointment.merge_appointments([a1, a2, a3, a4, a5, a6])
        print(merged)
        self.assertEqual(len(merged), 5)
        self.assertEqual(merged[3].price, Decimal(100.00))

    def test_two_mergeable(self):
        a1 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=14,
                                         minute=20,
                                         tzinfo=pytz.utc),
            length=timedelta(minutes=30),
            price=Decimal(50.00)
        )
        a1.save()

        a2 = Appointment(
            start_date_and_time=datetime(year=2018,
                                         month=3,
                                         day=2,
                                         hour=14,
                                         minute=50,
                                         tzinfo=pytz.utc),
            length=timedelta(minutes=30),
            price=Decimal(50.00)
        )
        a2.save()

        merged, unmerged = Appointment.merge_appointments([a1, a2])
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0].price, Decimal(100.00))
