import hashlib
from datetime import datetime, timedelta
from functools import partial

from django.contrib.auth.models import User
from django.db import models


class Patient(models.Model):
    date_of_birth = models.DateField()
    gender_choices = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('X', 'Other')
    )
    gender = models.CharField(max_length=1, choices=gender_choices)
    mobile = models.CharField(max_length=20)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        """Return the Patient's full name"""
        return "{} {}".format(self.user.first_name, self.user.last_name)


class Practitioner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100, blank=True, null=True)
    postcode = models.CharField(max_length=10)
    mobile = models.CharField(max_length=20)
    is_approved = models.BooleanField(default=False)
    bio = models.TextField()

    def __str__(self):
        """Return the Practitioner's full name"""
        return "{} {}".format(self.user.first_name, self.user.last_name)


def generate_session_id(salt, practitioner, patient, date_time):
    byte_string = str.encode(str(salt) + str(practitioner) + str(patient) + str(date_time))
    to_hash = hashlib.sha3_256(byte_string)
    hash_digest = to_hash.hexdigest()
    return hash_digest


class Appointment(models.Model):
    practitioner = models.ForeignKey(Practitioner,
                                     on_delete=models.SET_NULL,
                                     null=True)
    patient = models.ForeignKey(Patient,
                                on_delete=models.CASCADE,
                                null=True,
                                blank=True)
    start_date_and_time = models.DateTimeField()
    length = models.TimeField()
    """This is how long the appointment lasts"""
    practitioner_notes = models.TextField(blank=True)
    """These are notes left by the practitioner at the end of the appointment,
    that should only be visible to the practitioner"""
    patient_notes_by_practitioner = models.TextField(blank=True)
    """These are notes left by the practitioner at the end of the appointment,
    visible to the patient
    """
    patient_notes_before_meeting = models.TextField(blank=True)
    """These are notes left before the appointment by the patient,
    for the benefit of the practitioner
    """
    """session salt is used to ensure that the session id is less likely to collide.
    make_random_password is considered 'cryptographically secure' by Django
    """
    session_salt = models.CharField(max_length=255,
                                    default=partial(User.objects.make_random_password, 10), editable=False)
    """This is used to associate an appointment to a specific chat session.
    This id can then be used to join that chat session
    """
    session_id = models.CharField(max_length=255,
                                  default=partial(generate_session_id,
                                                  salt=session_salt,
                                                  practitioner=practitioner,
                                                  patient=patient,
                                                  date_time=start_date_and_time)
                                  , editable=False)

    def __str__(self):
        """Return a string representation of Appointment"""
        return "{} - {} for {}".format(str(self.practitioner),
                                       str(self.start_date_and_time),
                                       str(self.length))

    @classmethod
    def get_valid_appointments(cls, selected_date, selected_practitioner):
        selected_date_converted = datetime(selected_date.year, selected_date.month, selected_date.day)
        # TODO: Need to add a filter for appointment cut off times which may vary per practitioner
        if selected_date_converted < datetime.now():
            print("Date is less than current date")
            return []

        appointments = Appointment.objects.filter(start_date_and_time__day=selected_date.day
                                                  ).filter(start_date_and_time__month=selected_date.month
                                                           ).filter(start_date_and_time__year=selected_date.year
                                                                    ).filter(patient__isnull=True
                                                                             ).filter(
            practitioner_id=selected_practitioner)

        return appointments

    @classmethod
    def _add_time(cls, date_time, time):
        return date_time + timedelta(hours=time.hour, minutes=time.minute,
                                     seconds=time.minute)

    @classmethod
    def check_for_overlaps(cls, selected_appointments, selected_practitioner, patient_id):
        over_lap = cls.appointment_overlap_exists(selected_appointments, selected_practitioner, patient_id)

        if len(over_lap) > 0:
            return over_lap
        else:
            return []

    @classmethod
    def appointment_overlap_exists(cls, selected_appointments, selected_practitioner, patient_id):
        patient_obj = Patient.objects.get(pk=patient_id)
        existing_user_appointments = Appointment.objects.filter(patient_id=patient_obj.id)

        if len(existing_user_appointments) == 0:
            print("Patient doesnt have any appointments")
            return False

        # get the appointments the patient is trying to book, from the database
        appointments_to_book = []
        for _id in selected_appointments:
            appointments_to_book.append(Appointment.objects.get(pk=_id))

        # merges and sorts the lists
        merged_list = list(existing_user_appointments) + appointments_to_book

        return cls.get_overlaps(merged_list)

    @classmethod
    def get_overlaps(cls, list_of_appointments):
        list_of_appointments = sorted(list_of_appointments, key=lambda appointment: appointment.start_date_and_time)
        overlapping_appointments = []
        for i in range(0, len(list_of_appointments) - 1):
            # TODO: Might need to change length to duration if model changes to DurationField from TimeField
            cur_start_time = list_of_appointments[i].start_date_and_time
            cur_end_time = cls._add_time(cur_start_time, list_of_appointments[i].length)

            next_start_time = list_of_appointments[i + 1].start_date_and_time
            next_end_time = cls._add_time(next_start_time, list_of_appointments[i + 1].length)

            # limit to same day appointments
            if cur_start_time.date() == next_end_time.date():
                # first 2 clauses check for partial overlaps
                # next 2 check for complete overlaps i.e. 1 app. covers another completely
                if next_start_time < cur_end_time < next_end_time or \
                        cur_start_time < next_end_time < cur_end_time or \
                        next_start_time >= cur_start_time and next_end_time < cur_end_time or \
                        cur_start_time >= next_start_time and cur_end_time < next_end_time or \
                        cur_start_time == next_start_time:
                    overlapping_appointments.append(
                        [list_of_appointments[i], list_of_appointments[i + 1]])

        return overlapping_appointments
