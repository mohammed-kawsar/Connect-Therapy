from django.template.loader import render_to_string
from django.utils import timezone
from django.core.mail import send_mail

from connect_therapy.models import Appointment

from_email = 'support@connecttherapy.com'


def send_patient_appointment_reminders():
    appointments_today = Appointment.objects.filter(
        start_date_and_time__day=timezone.now().date(),
        patient__isnull=False
    )

    successfully_delivered = 0

    for appointment in appointments_today:
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
        successfully_delivered += send_mail(
            subject='Connect Therapy - Appointment Reminder',
            message=plain_text_message,
            from_email=from_email,
            recipient_list=[appointment.patient.user.email, ],
            fail_silently=True,
            html_message=html_message
        )

    print("{} emails not delivered".format(
        len(appointments_today) - successfully_delivered
        )
    )
