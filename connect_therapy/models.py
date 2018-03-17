import hashlib
from datetime import datetime, timedelta
from functools import partial

import pytz
from dateutil import parser
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
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
    email_confirmed = models.BooleanField(default=False)

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
    email_confirmed = models.BooleanField(default=False)
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
    length = models.DurationField(default=timedelta(minutes=30))
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
    def book_appointments(cls, appointments, patient):
        """
        :param appointments: An iterable of appointments to be booked
        :param patient: The patient booking the appointment
        """

        for app in appointments:
            app.patient = patient
            app.save()

        return True

    @classmethod
    def delete_appointments(cls, appointments):
        for app in appointments:
            app.delete()

    @classmethod
    def convert_dictionaries_to_appointments(cls, appointment_dict_list):
        """
        This method is used to convert a list of dictionaries - each on of which represents an appointment object
        - to a list of actual appointment objects. This is needed because to store an appointment using JSON (for sessions)
        we must store each appointment object as a dictionary object
        :param appointment_dict_list: List of dictionaries
        :return: List of appointments
        """
        appointments = []
        for app_dict in appointment_dict_list:
            if app_dict['id'] is None:
                appointment = Appointment(practitioner_id=app_dict['practitioner_id'],
                                          start_date_and_time=parser.parse(app_dict['start_date_and_time']),
                                          length=parser.parse(app_dict['length']),
                                          session_id=app_dict)
                appointments.append(appointment)
            else:
                appointments.append(Appointment.objects.get(pk=app_dict['id']))

        return appointments

    @classmethod
    def get_valid_appointments(cls, date, practitioner):

        selected_date_converted = datetime(date.year, date.month, date.day)
        # TODO: Need to add a filter for appointment cut off times which may vary per practitioner
        if selected_date_converted < datetime.now():
            print("Date is less than current date")
            return []

        appointments = Appointment.objects.filter(start_date_and_time__day=date.day
                                                  , start_date_and_time__month=date.month
                                                  , start_date_and_time__year=date.year
                                                  , patient__isnull=True
                                                  , practitioner_id=practitioner
                                                  ).order_by("start_date_and_time")
        """This method will return a list of valid appointments which can be booked by the user based on a given date
        and practitioner
        """
        return appointments

    @classmethod
    def _add_datetime_time(cls, date_time, time):
        """
        This method expects the first arg to be a datetime object and the second to be a time object
        It will then add the time to the date time object and return it
        :param date_time: Expects datetime object
        :param time: Expects the time object to come in the form of the timedelta
        used to model a DurationField. will not work as expected in any other case.
        :return:
        """

        other_date_time = date_time

        o_days, o_seconds = time.days, time.seconds
        other_hours = o_days * 24 + o_seconds // 3600
        other_minutes = (o_seconds % 3600) // 60
        other_seconds = o_seconds % 60
        end_date_time = other_date_time + timedelta(hours=other_hours, minutes=other_minutes, seconds=other_seconds)

        # print("First time: " + str(date_time))
        # print("Adding: " + str(time))
        # print("End time: " + str(end_date_time))
        # print("--------------------------------")
        return end_date_time

    @classmethod
    def _add_time(cls, start_date_and_time, time_1, time_2):
        time_1 = timedelta(hours=time_1.hour, minutes=time_1.minute,
                           seconds=time_1.minute)
        time_2 = timedelta(hours=time_2.hour, minutes=time_2.minute,
                           seconds=time_2.minute)

        total = time_1 + time_2
        seconds = total.total_seconds()
        hour = seconds / 3600
        minute = (seconds % 3600) / 60
        datetime_format = datetime(year=start_date_and_time.year, month=start_date_and_time.month,
                                   day=start_date_and_time.day,
                                   hour=int(hour), minute=int(minute))

        return datetime_format.time()

    @classmethod
    def check_validity(cls, selected_appointments_id, selected_practitioner):
        """Will check the validity of appointments selected.
        If they are valid, it will return the list of appointments from the database.
        Otherwise, false.
        """
        appointments_to_book = []
        selected_practitioner = Practitioner.objects.get(pk=selected_practitioner)
        for _id in selected_appointments_id:
            try:
                appointment = Appointment.objects.get(pk=_id)
                if appointment.start_date_and_time >= datetime.now(pytz.UTC) and \
                        appointment.practitioner == selected_practitioner and \
                        appointment.patient is None:
                    appointments_to_book.append(Appointment.objects.get(pk=_id))
                else:
                    return False
            except ObjectDoesNotExist:
                return False

        return appointments_to_book

    @classmethod
    def get_appointment_overlaps(cls, appointments_to_book, patient):
        """
        Will return
                - Tuple:
                        - First element true if no overlap, second list of valid appointments to be booked
                        - First element false if overlap, second list of overlapping appointments
        :param appointments_to_book: List of appointments to be booked
        :param patient: The patient for which the appoints should be booked for
        :return: Boolean - true if overlaps exist, if overlaps exist overlapping appointments original list otherwise
        """

        existing_user_appointments = Appointment.objects.filter(patient=patient)

        merged_list = list(existing_user_appointments) + appointments_to_book

        over_laps = cls._get_overlaps(merged_list)

        if len(over_laps) > 0:
            return False, over_laps
        else:
            return True, sorted(appointments_to_book, key=lambda appointment: appointment.start_date_and_time)

    @classmethod
    def get_appointment__practitioner_overlaps(cls, appointment, practitioner):
        """
        Will return
                - True if no overlap
                - Tuple:
                        - First element false if overlap, second list of overlapping appointments
        :param appointment: List of appointments to be booked
        :param practitioner: The practitioner who will be taking the appointment
        :return: Boolean - true if overlaps exist, if overlaps exist overlapping appointments original list otherwise
        """

        exisiting_appointments = Appointment.objects.filter(practitioner=practitioner)

        if len(exisiting_appointments) == 0:
            return True, []

        merged_list = list(exisiting_appointments)
        merged_list.append(appointment)

        over_laps = cls._get_overlaps(merged_list)

        if len(over_laps) > 0:
            return False, over_laps
        else:
            return True, []

    @classmethod
    def _get_overlaps(cls, appointments):
        """Passing in a list of appointments will allow this method to look for overlaps between appointments
        """
        list_of_appointments = sorted(appointments, key=lambda appointment: appointment.start_date_and_time)
        overlapping_appointments = []
        for i in range(0, len(list_of_appointments) - 1):
            # TODO: Might need to change length to duration if model changes to DurationField from TimeField
            cur_start_time = list_of_appointments[i].start_date_and_time
            cur_end_time = cls._add_datetime_time(cur_start_time, list_of_appointments[i].length)

            next_start_time = list_of_appointments[i + 1].start_date_and_time
            next_end_time = cls._add_datetime_time(next_start_time, list_of_appointments[i + 1].length)

            # limit to same day appointments
            if cur_start_time.date() == next_end_time.date():
                print("Current start time: " + str(cur_start_time))
                print("Current end time: " + str(cur_end_time))
                print("Next start time: " + str(next_start_time))
                print("Next end time: " + str(next_end_time))
                print("---------------------------------------------")
                # first 2 clauses check for partial overlaps
                # next 2 check for complete overlaps i.e. 1 app. covers another completely
                if next_start_time < cur_end_time <= next_end_time or \
                        cur_start_time < next_end_time < cur_end_time or \
                        next_start_time >= cur_start_time and next_end_time < cur_end_time or \
                        cur_start_time >= next_start_time and cur_end_time < next_end_time or \
                        cur_start_time == next_start_time:
                    overlapping_appointments.append(
                        [list_of_appointments[i], list_of_appointments[i + 1]])

        return overlapping_appointments

    @classmethod
    def merge_appointments(cls, appointments):
        """
        This method will merge any consecutive appointments. The start time of one appointment must match with the
        end time of another exactly - in order for them to be merged. If none can be merged, then the original list of
        appointments is returned.
        :param appointments: The list of appointments to be merged
        :return: List of merged appointments if it was possible to merge with a list of appointments which have been
        merged so these can be deleted or otherwise dealt with.
        """
        stack = []
        merged_apps = []
        if len(appointments) <= 1:
            return appointments, []
        else:
            list_of_appointments = sorted(appointments, key=lambda appointment: appointment.start_date_and_time)
            for app in list_of_appointments:
                if len(stack) == 0:
                    stack.append(app)
                else:
                    i_from_s = stack.pop()

                    i_end_time = cls._add_datetime_time(i_from_s.start_date_and_time, i_from_s.length)

                    if i_end_time == app.start_date_and_time:

                        merged = Appointment(practitioner=app.practitioner,
                                             start_date_and_time=i_from_s.start_date_and_time,
                                             length=cls._add_time(i_from_s.start_date_and_time, i_from_s.length,
                                                                  app.length))

                        stack.append(merged)
                        merged_apps.append(i_from_s)
                        merged_apps.append(app)
                    else:
                        stack.append(i_from_s)
                        stack.append(app)

        merged_apps = cls._remove_duplicates(merged_apps)
        return stack, merged_apps

    @classmethod
    def _remove_duplicates(cls, appointments):
        for app in appointments:
            for other_app in appointments:
                if app.start_date_and_time == other_app.start_date_and_time and app != other_app:
                    appointments.remove(other_app)

        return appointments


class File(models.Model):
    file = models.FileField()
