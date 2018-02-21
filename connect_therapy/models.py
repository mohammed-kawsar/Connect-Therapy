from django.db import models
from django.contrib.auth.models import User
from functools import partial
from datetime import datetime, timedelta
import hashlib


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
    def add_time(cls, date_time, time):
        return date_time + timedelta(hours=time.hour, minutes=time.minute,
                                     seconds=time.minute)

    @classmethod
    def is_appointment_valid(cls, selected_appointments, selected_practitioner, patient_id):
        # get existing up-coming appointments
        cls.appointment_overlap_exists(selected_appointments, selected_practitioner, patient_id)

    @classmethod
    def appointment_overlap_exists(cls, selected_appointments, selected_practitioner, patient_id):
        patient_obj = Patient.objects.get(pk=patient_id)
        existing_user_appointments = Appointment.objects.filter(patient_id=patient_obj.id)
        print(patient_obj)
        if len(existing_user_appointments) == 0:
            print("Patient doesnt have any appointments")
            return False

        appointments_to_book = []
        for id in selected_appointments:
            appointments_to_book.append(Appointment.objects.get(pk=id))

        # merges and sorts the lists
        merged_list = list(existing_user_appointments) + appointments_to_book
        merged_list = sorted(merged_list, key=lambda appointment: appointment.start_date_and_time)
        print(merged_list)
        # gets overlapping appointments
        overlapping_appointments = []
        for i in range(0, len(merged_list) - 1):
            cur_start_time = merged_list[i].start_date_and_time
            cur_end_time = cls.add_time(cur_start_time, merged_list[i].length)

            next_start_time = merged_list[i + 1].start_date_and_time
            next_end_time = cls.add_time(next_start_time, merged_list[i + 1].length)

            # TODO: Missing case, when either task completely envelopes another i.e. last for the full duration

            if next_start_time < cur_end_time < next_end_time or \
                    cur_start_time < next_end_time < cur_end_time or \
                    cur_start_time == next_start_time:
                overlapping_appointments.append(
                    [merged_list[i].start_date_and_time, merged_list[i + 1].start_date_and_time])

        print(overlapping_appointments)
        return overlapping_appointments
