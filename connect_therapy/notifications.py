from connect_therapy.emails import *
from connect_therapy import sms


def appointment_booked(appointment):
    send_practitioner_appointment_booked(appointment)
    send_patient_appointment_booked(appointment)
    sms.send_appointment_booked(appointment.patient, appointment)
    sms.send_appointment_booked(appointment.practitioner, appointment)


def multiple_appointments_booked(appointments):
    for appointment in appointments:
        appointment_booked(appointment)


def reminders():
    send_patient_appointment_reminders()
    send_practitioner_appointment_reminders()
    sms.send_patient_appointment_reminders()
    sms.send_practitioner_appointment_reminders()


def appointment_cancelled_by_patient(patient, appointment, under_24h=False):
    """This must be called BEFORE the appointment is actually cancelled"""
    if under_24h:
        send_patient_cancelled_under_24_hours(patient, appointment)
        send_practitioner_patient_cancelled_in_under_24_hours(appointment)
    else:
        send_patient_cancelled_in_good_time(patient, appointment)
        send_practitioner_patient_cancelled_in_good_time(appointment)
    sms.send_appointment_cancelled(appointment.patient, appointment)
    sms.send_appointment_cancelled(appointment.practitioner, appointment)


def appointment_cancelled_by_practitioner(appointment):
    """This must be called BEFORE the appointment is actually cancelled"""
    if appointment.patient:
        send_patient_practitioner_has_cancelled(appointment)
        sms.send_appointment_cancelled(appointment.patient, appointment)
    send_practitioner_cancelled(appointment)
    sms.send_appointment_cancelled(appointment.practitioner, appointment)
