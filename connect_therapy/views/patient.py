from datetime import timedelta, time

from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, views as auth_views, \
    update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic
from django.views.generic import FormView, DetailView, UpdateView
from django.views.generic import TemplateView
from django.views.generic.edit import FormMixin

from connect_therapy import notifications
from connect_therapy.forms.patient import AppointmentDateSelectForm
from connect_therapy.forms.patient import PatientSignUpForm, PatientLoginForm, \
    PatientNotesBeforeForm, PatientEditMultiForm
from connect_therapy.models import Patient, Appointment
from connect_therapy.models import Practitioner
from connect_therapy.views.views import FileDownloadView


class PatientSignUpView(FormView):
    form_class = PatientSignUpForm
    template_name = 'connect_therapy/patient/signup.html'
    success_url = reverse_lazy('connect_therapy:patient-signup-success')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.username = user.email
        user.save()
        patient = Patient(user=user,
                          date_of_birth=form.cleaned_data['date_of_birth'],
                          gender=form.cleaned_data['gender'],
                          mobile=form.cleaned_data['mobile']
                          )
        patient.save()
        user = authenticate(username=form.cleaned_data['email'],
                            password=form.cleaned_data['password1']
                            )
        login(request=self.request, user=user)
        return super().form_valid(form)


class PatientLoginView(auth_views.LoginView):
    template_name = 'connect_therapy/patient/login.html'
    authentication_form = PatientLoginForm

    def get_success_url(self):
        return reverse_lazy('connect_therapy:patient-login-success')


class PatientMyAppointmentsView(generic.TemplateView):
    template_name = 'connect_therapy/patient/my-appointments.html'

    model = Appointment

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['future_appointments'] = Appointment.objects.filter(
            start_date_and_time__gte=timezone.now(),
            patient=self.request.user.patient
        ).order_by('-start_date_and_time')
        context['past_appointments'] = Appointment.objects.filter(
            start_date_and_time__lt=timezone.now(),
            patient=self.request.user.patient
        ).order_by('-start_date_and_time')
        return context


class PatientNotesBeforeView(LoginRequiredMixin, FormView):
    form_class = PatientNotesBeforeForm
    template_name = 'connect_therapy/patient/notes-before-appointment.html'
    success_url = reverse_lazy('connect_therapy:patient-my-appointments')
    appointment = Appointment

    def form_valid(self, form):
        self.appointment.patient_notes_before_meeting = \
            form.cleaned_data['patient_notes_before_meeting']
        self.appointment.save()
        return super().form_valid(form)

    def get(self, request, appointment_id):
        self.appointment = get_object_or_404(Appointment, pk=appointment_id)

        from connect_therapy.views.views import FileDownloadView
        files_for_appointment = FileDownloadView.get_files_from_folder(self, str(self.appointment.id))
        downloadable_file_list = FileDownloadView.generate_pre_signed_url_for_each(self, files_for_appointment)

        return render(request, self.get_template_names(), {'appointment': self.appointment,
                                                           'form': self.get_form(),
                                                           "downloadable_files": downloadable_file_list})

    def post(self, request, appointment_id):
        self.appointment = get_object_or_404(Appointment, pk=appointment_id)
        return super().post(request)


class PatientCancelAppointmentView(FormMixin, DetailView):
    model = Appointment
    form_class = forms.Form
    template_name = 'connect_therapy/patient/cancel-appointment.html'

    def get_success_url(self):
        return reverse_lazy('connect_therapy:patient-my-appointments')

    def get_context_data(self, **kwargs):
        context = super(PatientCancelAppointmentView, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def form_valid(self, form):
        # Here, we would record the user's interest using the message
        # passed in form.cleaned_data['message']
        notifications.appointment_cancelled_by_patient(
            self.object.patient,
            self.object,
            self.object.start_date_and_time < timezone.now() + timedelta(hours=24)
        )
        self.object.patient = None
        self.object.save()
        self.split_merged_appointment()

        return super(PatientCancelAppointmentView, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid() and self.object.start_date_and_time > timezone.now():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def split_merged_appointment(self):
        original_length = self.object.length

        if original_length.minute == 30:
            return

        self.object.length = time(minute=30)
        self.object.patient = None
        self.object.price = price = Appointment._meta.fields['price'].get_default()
        number_of_appointments = \
            (original_length.hour * 60 + original_length.minute) // 30
        for i in range(1, number_of_appointments):
            appointment = Appointment(
                practitioner=self.object.practitioner,
                patient=None,
                length=time(minute=30),
                start_date_and_time=self.object.start_date_and_time
                                    + timedelta(minutes=30 * i),
                price=Appointment._meta.fields['price'].get_default()
            )
            appointment.save()
            self.object.save()


class PatientPreviousNotesView(LoginRequiredMixin, generic.DetailView):
    login_url = reverse_lazy('connect_therapy:patient-appointment-notes')
    model = Appointment
    template_name = 'connect_therapy/patient/appointment-notes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        files_for_appointment = FileDownloadView.get_files_from_folder(self, str(self.object.id))
        downloadable_file_list = FileDownloadView.generate_pre_signed_url_for_each(self, files_for_appointment)

        context['downloadable_files'] = downloadable_file_list

        return context


class ViewBookableAppointmentsView(UserPassesTestMixin, DetailView):
    template_name = "connect_therapy/patient/bookings/view-available.html"
    model = Practitioner
    login_url = reverse_lazy('connect_therapy:patient-login')

    def test_func(self):
        if self.request.user.is_anonymous:
            return False
        try:
            patient = Patient.objects.get(user=self.request.user)
            return True
        except Patient.DoesNotExist:
            return False

    def get(self, request, pk):
        # define the object for the detail view
        self.object = self.get_object()
        form = AppointmentDateSelectForm
        return render(self.request,
                      self.template_name,
                      context={"form": form,
                               "object": self.object})

    def post(self, request, pk):
        self.object = self.get_object()
        practitioner = Practitioner.objects.filter(pk=pk)
        form = AppointmentDateSelectForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            # pk = practitioner id
            appointments = Appointment.get_valid_appointments(date, pk)

            return render(self.request,
                          self.template_name,
                          context={"form": form,
                                   "appointments": appointments,
                                   "object": self.get_object()})
        else:
            return self.get(request)


class ReviewSelectedAppointmentsView(UserPassesTestMixin, TemplateView):
    template_name = 'connect_therapy/patient/bookings/review-selection.html'
    login_url = reverse_lazy('connect_therapy:patient-login')
    patient = Patient()

    def test_func(self):
        if self.request.user.is_anonymous:
            return False
        try:
            self.patient = Patient.objects.get(user=self.request.user)
            return True
        except Patient.DoesNotExist:
            return False

    def post(self, request, *args, **kwargs):
        app_ids = request.POST.getlist('app_id')
        practitioner_id = kwargs['pk']

        if len(app_ids) == 0:
            messages.warning(request, "You haven't selected any appointments")
            return ViewBookableAppointmentsView.get(self, request, practitioner_id)

        return self._deal_with_appointments(request=request, app_ids=app_ids, practitioner_id=practitioner_id)

    def _deal_with_appointments(self, request, app_ids, practitioner_id):
        valid_appointments = Appointment.check_validity(selected_appointments_id=app_ids,
                                                        selected_practitioner=practitioner_id)

        if valid_appointments is not False:
            overlap_free, appointments_to_book = Appointment.get_appointment_overlaps(valid_appointments,
                                                                                      patient=self.patient)
            if overlap_free is False:
                # valid appointments but overlap exists
                clashes = appointments_to_book
                return render(request, self.get_template_names(), context={"clashes": clashes})
            else:
                # all valid
                bookable_appointments, merged_appointments = Appointment.merge_appointments(appointments_to_book)

                # show user message about merged appointments
                if len(merged_appointments) == 1:
                    messages.success(request, str(len(merged_appointments)) + " appointment was merged")
                elif len(merged_appointments) > 1:
                    messages.success(request, str(len(merged_appointments)) + " appointments were merged")

                # add to session data - used by the checkout
                request.session['bookable_appointments'] = Appointment.appointments_to_dictionary_list(
                    bookable_appointments)
                request.session['merged_appointments'] = Appointment.appointments_to_dictionary_list(
                    merged_appointments)
                request.session['patient_id'] = self.patient.id
                return render(request, self.get_template_names(), {"bookable_appointments": bookable_appointments,
                                                                   "merged_appointments": merged_appointments,
                                                                   "practitioner_id": practitioner_id})
        else:
            # appointments not valid
            invalid_appointments = True
            return render(request, self.get_template_names(), context={"invalid_appointments": invalid_appointments})


class CheckoutView(UserPassesTestMixin, TemplateView):
    login_url = reverse_lazy('connect_therapy:patient-login')
    template_name = "connect_therapy/patient/bookings/checkout.html"
    patient = Patient()

    def test_func(self):
        if self.request.user.is_anonymous:
            return False
        try:
            self.patient = Patient.objects.get(user=self.request.user)
            return True
        except Patient.DoesNotExist:
            return False

    def get(self, request, *args, **kwargs):
        appointments_to_book = []
        try:
            appointment_dictionary = request.session['bookable_appointments']
        except KeyError:
            return render(request, self.get_template_names(), {"appointments": appointments_to_book})
        if appointment_dictionary is None:
            return render(request, self.get_template_names(), {"appointments": appointments_to_book})
        appointments_to_book = Appointment.convert_dictionaries_to_appointments(appointment_dictionary)
        return render(request, self.get_template_names(), {"appointments": appointments_to_book})

    def post(self, request, *args, **kwargs):
        # session_id would only be passed in to identify an appointment to delete
        if 'session_id' in request.POST:
            list_of_appointments = request.session['bookable_appointments']
            if list_of_appointments is None:
                return self.get(request, *args, **kwargs)
            for app in list_of_appointments:
                if app['session_id'] == request.POST['session_id']:
                    request.session['bookable_appointments'] = list_of_appointments.remove(app)
                    return self.get(request, *args, *kwargs)
        elif 'checkout' in request.POST:
            # TODO: Add payment gateway stuff here...probably

            appointment_dictionary = request.session['bookable_appointments']
            if appointment_dictionary is None:
                return self.get(request, *args, **kwargs)
            appointments_to_book = Appointment.convert_dictionaries_to_appointments(appointment_dictionary)

            # first delete the appointments we merged, if any
            merged_dictionary = request.session['merged_appointments']
            if merged_dictionary is None:
                # no merges where made so we dont need to do anything with them
                pass
            else:
                merged_appointment_list = Appointment.convert_dictionaries_to_appointments(merged_dictionary)
                Appointment.delete_appointments(merged_appointment_list)

            # go ahead and book those appointments
            if Appointment.book_appointments(appointments_to_book, self.patient):
                notifications.multiple_appointments_booked(appointments_to_book)  # call method from notifications.py
                return render(request, "connect_therapy/patient/bookings/booking-success.html", {})
            else:
                return HttpResponse("Failed to book. Patient object doesnt exist.")


class PatientProfileView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'connect_therapy/patient/profile.html'

    @login_required
    def view_profile(self, request):
        user = request.user
        args = {'user': user}
        return render(request, args)


class PatientEditDetailsView(LoginRequiredMixin, UpdateView):
    model = Patient
    template_name = 'connect_therapy/patient/edit-profile.html'
    form_class = PatientEditMultiForm
    success_url = reverse_lazy('connect_therapy:patient-profile')

    def form_valid(self, form):
        self.object.user.username = form.cleaned_data['user']['email']
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        try:
            user = User.objects.get(username=form.cleaned_data['user']['email'])
            if user == self.object.user:
                return self.form_valid(form)
        except User.DoesNotExist:
            # if User.objects.get(email=user.email) == user.email:
            #     return self.form_valid(form)
            if form.is_valid():
                return self.form_valid(form)

        return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super(PatientEditDetailsView, self).get_form_kwargs()
        kwargs.update(instance={
            'user': self.object.user,
            'patient': self.object,
        })
        return kwargs


class ViewAllPractitionersView(UserPassesTestMixin, generic.ListView):
    login_url = reverse_lazy('connect_therapy:patient-login')
    model = Practitioner
    template_name = 'connect_therapy/patient/bookings/list-practitioners.html'
    context_object_name = "practitioners"

    def test_func(self):
        logged_in = self.request.user.is_authenticated

        if not logged_in:
            return False

        from django.core.exceptions import ObjectDoesNotExist
        try:
            Practitioner.objects.get(user=self.request.user)
            not_practitioner = False
        except ObjectDoesNotExist:
            not_practitioner = True

        return not_practitioner and logged_in;

    def get_queryset(self):
        return Practitioner.objects.all()


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect(reverse_lazy('connect_therapy:patient-profile'))
        else:
            return redirect(reverse_lazy(
                'connect_therapy:patient-change-password')
            )
    else:
        form = PasswordChangeForm(user=request.user)
        args = {'form': form}
        return render(request, 'connect_therapy/patient/change-password.html', args)
