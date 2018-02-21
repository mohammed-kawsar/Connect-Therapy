from django.db import models
from django.contrib.auth.models import User
from functools import partial
import hashlib
from django.db.models.signals import post_save


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


# def create_profile(sender, **kwargs):
#     if kwargs['created']:
#         user_profile = Practitioner.objects.create(user = kwargs['instance'])
#
#
# post_save.connect(create_profile, sender=User)

