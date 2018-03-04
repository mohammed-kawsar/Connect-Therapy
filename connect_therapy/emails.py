from threading import Thread

from django.template.loader import render_to_string
from django.utils import timezone
from django.core.mail import send_mail

from connect_therapy.models import Appointment

from_email = 'support@connecttherapy.com'


def send_password_reset(user, link):
    context = {
        'user': user,
        'link': link
    }
    plain_text_message = render_to_string(
        'connect_therapy/emails/plain-text/password-reset.txt',
        context
    )
    html_message = render_to_string(
        'connect_therapy/emails/html/password-reset.html',
        context
    )
    send_mail(
        subject='Connect Therapy - Password Reset',
        message=plain_text_message,
        from_email=from_email,
        recipient_list=[user.email, ],
        html_message=html_message
    )


def send_patient_appointment_booked(appointment):
    context = {
        'user': appointment.patient.user,
        'appointment': appointment
    }
    plain_text_message = render_to_string(
        'connect_therapy/emails/plain-text/'
        'patient-appointment-booked.txt',
        context
    )
    html_message = render_to_string(
        'connect_therapy/emails/html/patient-appointment-booked.html',
        context
    )
    send_mail(
        subject='Connect Therapy - Appointment Booked',
        message=plain_text_message,
        from_email=from_email,
        recipient_list=[appointment.patient.user.email, ],
        html_message=html_message
    )


def send_patient_appointment_reminders():
    appointments_today = Appointment.objects.filter(
        start_date_and_time__day=timezone.now().date(),
        patient__isnull=False
    )

    def send_reminder(appointment):
        context = {
            'user': appointment.patient.user,
            'appointment': appointment
        }
        plain_text_message = render_to_string(
            'connect_therapy/emails/plain-text/'
            'patient-appointment-reminder.txt',
            context
        )
        html_message = render_to_string(
            'connect_therapy/emails/html/patient-appointment-reminder.html',
            context
        )
        send_mail(
            subject='Connect Therapy - Appointment Reminder',
            message=plain_text_message,
            from_email=from_email,
            recipient_list=[appointment.patient.user.email, ],
            fail_silently=True,
            html_message=html_message
        )

    threads = map(
        lambda appointment: Thread(
            target=send_reminder,
            args=(appointment, )
        ),
        appointments_today
    )

    for thread in threads:
        thread.start()

    return threads


def send_patient_cancelled_in_good_time(patient, appointment):
    context = {
        'user': patient.user,
        'appointment': appointment
    }
    plain_text_message = render_to_string(
        'connect_therapy/emails/plain-text/'
        'patient-cancelled-in-good-time.txt',
        context
    )
    html_message = render_to_string(
        'connect_therapy/emails/html/patient-cancelled-in-good-time.html',
        context
    )
    send_mail(
        subject='Connect Therapy - Appointment Cancelled',
        message=plain_text_message,
        from_email=from_email,
        recipient_list=[patient.user.email, ],
        html_message=html_message
    )


def send_patient_cancelled_under_24_hours(patient, appointment):
    context = {
        'user': patient.user,
        'appointment': appointment
    }
    plain_text_message = render_to_string(
        'connect_therapy/emails/plain-text/'
        'patient-cancelled-under-24-hours.txt',
        context
    )
    html_message = render_to_string(
        'connect_therapy/emails/html/patient-cancelled-under-24-hours.html',
        context
    )
    send_mail(
        subject='Connect Therapy - Appointment Cancelled',
        message=plain_text_message,
        from_email=from_email,
        recipient_list=[patient.user.email, ],
        html_message=html_message
    )


def send_patient_confirm_email(patient, link):
    context = {
        'user': patient.user,
        'link': link
    }
    plain_text_message = render_to_string(
        'connect_therapy/emails/plain-text/patient-confirm-email.txt',
        context
    )
    html_message = render_to_string(
        'connect_therapy/emails/html/patient-confirm-email.html',
        context
    )
    send_mail(
        subject='Connect Therapy - Confirm Email',
        message=plain_text_message,
        from_email=from_email,
        recipient_list=[patient.user.email, ],
        html_message=html_message
    )


def send_patient_email_confirmed(patient):
    context = {
        'user': patient.user
    }
    plain_text_message = render_to_string(
        'connect_therapy/emails/plain-text/patient-email-confirmed.txt',
        context
    )
    html_message = render_to_string(
        'connect_therapy/emails/html/patient-email-confirmed.html',
        context
    )
    send_mail(
        subject='Connect Therapy - Email Confirmed',
        message=plain_text_message,
        from_email=from_email,
        recipient_list=[patient.user.email, ],
        html_message=html_message
    )


def send_patient_practitioner_has_cancelled(appointment, message=None):
    """This must be called BEFORE deleting the appointment"""
    context = {
        'user': appointment.patient.user,
        'message': message
    }
    plain_text_message = render_to_string(
        'connect_therapy/emails/plain-text/'
        'patient-practitioner-has-cancelled.txt',
        context
    )
    html_message = render_to_string(
        'connect_therapy/emails/html/patient-practitioner-has-cancelled.html',
        context
    )
    send_mail(
        subject='Connect Therapy - Your appointment has been cancelled',
        message=plain_text_message,
        from_email=from_email,
        recipient_list=[appointment.patient.user.email, ],
        html_message=html_message
    )


def send_practitioner_appointment_booked(appointment):
    context = {
        'user': appointment.practitioner.user,
        'appointment': appointment
    }
    plain_text_message = render_to_string(
        'connect_therapy/emails/plain-text/'
        'practitioner-appointment-booked.txt',
        context
    )
    html_message = render_to_string(
        'connect_therapy/emails/html/practitioner-appointment-booked.html',
        context
    )
    send_mail(
        subject='Connect Therapy - Appointment Booking',
        message=plain_text_message,
        from_email=from_email,
        recipient_list=[appointment.patient.user.email, ],
        html_message=html_message
    )


def send_practitioner_appointment_reminders():
    appointments_today = Appointment.objects.filter(
        start_date_and_time__day=timezone.now().date(),
        patient__isnull=False
    )

    def send_reminder(appointment):
        context = {
            'user': appointment.practitioner.user,
            'appointment': appointment
        }
        plain_text_message = render_to_string(
            'connect_therapy/emails/plain-text/'
            'practitioner-appointment-reminder.txt',
            context
        )
        html_message = render_to_string(
            'connect_therapy/emails/html/practitioner-appointment-reminder.html',
            context
        )
        send_mail(
            subject='Connect Therapy - Appointment Reminder',
            message=plain_text_message,
            from_email=from_email,
            recipient_list=[appointment.practitioner.user.email, ],
            fail_silently=True,
            html_message=html_message
        )

    threads = map(
        lambda appointment: Thread(
            target=send_reminder,
            args=(appointment, )
        ),
        appointments_today
    )

    for thread in threads:
        thread.start()

    return threads


def send_practitioner_approved(practitioner):
    context = {
        'user': practitioner.user,
    }
    plain_text_message = render_to_string(
        'connect_therapy/emails/plain-text/'
        'practitioner-approved.txt',
        context
    )
    html_message = render_to_string(
        'connect_therapy/emails/html/practitioner-approved.html',
        context
    )
    send_mail(
        subject="Connect Therapy - You've been approved",
        message=plain_text_message,
        from_email=from_email,
        recipient_list=[practitioner.user.email, ],
        html_message=html_message
    )


def send_practitioner_cancelled(appointment):
    context = {
        'user': appointment.practitioner.user,
        'appointment': appointment
    }
    plain_text_message = render_to_string(
        'connect_therapy/emails/plain-text/'
        'practitioner-cancelled.txt',
        context
    )
    html_message = render_to_string(
        'connect_therapy/emails/html/practitioner-cancelled.html',
        context
    )
    send_mail(
        subject="Connect Therapy - Cancellation confirmation",
        message=plain_text_message,
        from_email=from_email,
        recipient_list=[appointment.practitioner.user.email, ],
        html_message=html_message
    )


def send_practitioner_confirm_email(practitioner, link):
    context = {
        'user': practitioner.user,
        'link': link
    }
    plain_text_message = render_to_string(
        'connect_therapy/emails/plain-text/'
        'practitioner-confirm-email.txt',
        context
    )
    html_message = render_to_string(
        'connect_therapy/emails/html/practitioner-confirm-email.html',
        context
    )
    send_mail(
        subject="Connect Therapy - Confirm Email",
        message=plain_text_message,
        from_email=from_email,
        recipient_list=[practitioner.user.email, ],
        html_message=html_message
    )


def send_practitioner_email_confirmed(practitioner):
    context = {
        'user': practitioner.user
    }
    plain_text_message = render_to_string(
        'connect_therapy/emails/plain-text/practitioner-email-confirmed.txt',
        context
    )
    html_message = render_to_string(
        'connect_therapy/emails/html/practitioner-email-confirmed.html',
        context
    )
    send_mail(
        subject='Connect Therapy - Email Confirmed',
        message=plain_text_message,
        from_email=from_email,
        recipient_list=[practitioner.user.email, ],
        html_message=html_message
    )


def send_practitioner_patient_cancelled_in_good_time(appointment):
    """This must be called BEFORE the appointment is actually cancelled"""
    context = {
        'user': appointment.practitioner.user,
        'appointment': appointment
    }
    plain_text_message = render_to_string(
        'connect_therapy/emails/plain-text/'
        'practitioner-patient-cancelled-in-good-time.txt',
        context
    )
    html_message = render_to_string(
        'connect_therapy/emails/html/practitioner-patient-cancelled-in-good-time.html',
        context
    )
    send_mail(
        subject='Connect Therapy - Appointment Cancelled',
        message=plain_text_message,
        from_email=from_email,
        recipient_list=[appointment.practitioner.user.email, ],
        html_message=html_message
    )


def send_practitioner_patient_cancelled_in_under_24_hours(appointment):
    """This must be called BEFORE the appointment is actually cancelled"""
    context = {
        'user': appointment.practitioner.user,
        'appointment': appointment
    }
    plain_text_message = render_to_string(
        'connect_therapy/emails/plain-text/'
        'practitioner-patient-cancelled-in-under-24-hours.txt',
        context
    )
    html_message = render_to_string(
        'connect_therapy/emails/html/'
        'practitioner-patient-cancelled-in-under-24-hours.html',
        context
    )
    send_mail(
        subject='Connect Therapy - Appointment Cancelled',
        message=plain_text_message,
        from_email=from_email,
        recipient_list=[appointment.practitioner.user.email, ],
        html_message=html_message
    )
