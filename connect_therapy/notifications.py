from threading import Thread
from connect_therapy.emails import *


def appointment_booked(appointment):
    threads = [
        Thread(target=send_patient_appointment_booked, args=(appointment, )),
        Thread(target=send_practitioner_appointment_booked,
               args=(appointment, )
               ),
    ]

    for thread in threads:
        thread.start()

    return threads


def multiple_appointments_booked(appointments):
    threads = map(
        lambda appointment: Thread(
            target=appointment_booked,
            args=(appointment,)
        ),
        appointments
    )

    for thread in threads:
        thread.start()

    return threads


def reminders():
    threads = [
        Thread(target=send_patient_appointment_reminders),
        Thread(target=send_practitioner_appointment_reminders),
    ]

    for thread in threads:
        thread.start()

    return threads


def appointment_cancelled_by_patient(patient, appointment, under_24h=False):
    """This must be called BEFORE the appointment is actually cancelled"""
    if under_24h:
        send_patient_cancelled_under_24_hours(patient, appointment)
        send_practitioner_patient_cancelled_in_under_24_hours(appointment)
    else:
        send_patient_cancelled_in_good_time(patient, appointment)
        send_practitioner_patient_cancelled_in_good_time(appointment)


def appointment_cancelled_by_practitioner(appointment):
    """This must be called BEFORE the appointment is actually cancelled"""
    send_patient_practitioner_has_cancelled(appointment)
    send_practitioner_cancelled(appointment)