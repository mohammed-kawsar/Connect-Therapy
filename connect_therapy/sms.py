from datetime import timedelta

from django.template.loader import render_to_string
from django.utils import timezone
from twilio.rest import Client

from connect_therapy.models import Appointment
from mysite.settings import TWILIO_ACC_SID, TWILIO_AUTH_TOKEN, \
    TWILIO_PHONE_NUMBER


twilio_client = Client(TWILIO_ACC_SID, TWILIO_AUTH_TOKEN)


def __send_sms(number, body):
    number = clean_phone_number(number)
    twilio_client.api.account.messages.create(
        to=number,
        from_=TWILIO_PHONE_NUMBER,
        body=body
    )


def clean_phone_number(number):
    number = number.replace(' ', '')
    if number[0] == '0':
        number = '+44' + number[1:]
    return number


def send_appointment_booked(recipient, appointment):
    context = {
        'appointment': appointment
    }
    body = render_to_string(
        'connect_therapy/sms/appointment-confirmation.txt',
        context
    )
    __send_sms(recipient.mobile, body)


def send_appointment_cancelled(recipient, appointment):
    """This must be called BEFORE the appointment is actually cancelled"""
    context = {
        'appointment': appointment
    }
    body = render_to_string(
        'connect_therapy/sms/appointment-cancelled.txt',
        context
    )
    __send_sms(recipient.mobile, body)


def send_appointment_reminder(recipient, appointment):
    """This must be called BEFORE the appointment is actually cancelled"""
    context = {
        'appointment': appointment
    }
    body = render_to_string(
        'connect_therapy/sms/appointment-reminder.txt',
        context
    )
    __send_sms(recipient.mobile, body)


def send_patient_appointment_reminders():
    appointments_today = Appointment.objects.filter(
        start_date_and_time__gt=timezone.now().date(),
        start_date_and_time__lte=timezone.now().date() + timedelta(days=1)
    ).exclude(patient=None)

    for appointment in appointments_today:
        send_appointment_reminder(appointment.patient, appointment)


def send_practitioner_appointment_reminders():
    appointments_today = Appointment.objects.filter(
        start_date_and_time__gt=timezone.now().date(),
        start_date_and_time__lte=timezone.now().date() + timedelta(days=1)
    ).exclude(patient=None)

    for appointment in appointments_today:
        send_appointment_reminder(appointment.practitioner, appointment)
