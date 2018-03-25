from datetime import timedelta, datetime
from decimal import Decimal

import pytz
from django.test import TestCase

from connect_therapy.models import Appointment


class TestAppointmentSplit(TestCase):
    def test_split_merged_appointment_into_3(self):
        start_date_and_time = datetime(year=2018,
                                       month=3,
                                       day=11,
                                       hour=12,
                                       minute=00)
        appointment = Appointment(
            start_date_and_time=start_date_and_time,
            length=timedelta(hours=1, minutes=30))

        appointment.save()
        Appointment.split_merged_appointment(appointment)
        new_appointments = Appointment.objects.filter(
            start_date_and_time__gte=start_date_and_time,
            start_date_and_time__lte=start_date_and_time + timedelta(minutes=60)
        )
        self.assertEqual(len(new_appointments), 3)

        for appointment in new_appointments:
            self.assertEqual(appointment.length, timedelta(minutes=30))

            self.assertEquals(appointment.price, Decimal(Appointment._meta.get_field('price').get_default()))

    def test_split_merged_appointment_into_6(self):
        start_date_and_time = datetime(year=2018,
                                       month=3,
                                       day=11,
                                       hour=12,
                                       minute=00)
        appointment = Appointment(start_date_and_time=start_date_and_time,
                                  length=timedelta(hours=3))

        appointment.save()
        Appointment.split_merged_appointment(appointment)
        new_appointments = Appointment.objects.filter(
            start_date_and_time__gte=start_date_and_time,
            start_date_and_time__lte=start_date_and_time + timedelta(hours=3)
        )
        self.assertEqual(len(new_appointments), 6)

        for appointment in new_appointments:
            self.assertEqual(appointment.length, timedelta(minutes=30))

            self.assertEquals(appointment.price, Decimal(Appointment._meta.get_field('price').get_default()))

    def test_split_merged_appointment_when_no_splits_should_happen(self):
        start_date_and_time = datetime(year=2018,
                                       month=3,
                                       day=11,
                                       hour=12,
                                       minute=00)
        appointment = Appointment(start_date_and_time=start_date_and_time,
                                  length=timedelta(minutes=30))
        appointment.save()
        Appointment.split_merged_appointment(appointment)
        new_appointments = Appointment.objects.filter(
            start_date_and_time__gte=start_date_and_time,
            start_date_and_time__lte=start_date_and_time + timedelta(minutes=30)
        )
        self.assertEqual(len(new_appointments), 1)
        for appointment in new_appointments:
            self.assertEqual(appointment.length, timedelta(minutes=30))
