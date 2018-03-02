from django.contrib import messages
from django.contrib.auth import views as auth_views, authenticate, login
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic
from django.views.generic import FormView, DetailView, TemplateView
from django.views.generic.edit import FormMixin

from connect_therapy.forms import *
from connect_therapy.models import Patient, Practitioner, Appointment


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


class ChatView(UserPassesTestMixin, DetailView):
    model = Appointment
    template_name = 'connect_therapy/chat.html'
    login_url = reverse_lazy('connect_therapy:patient-login')

    def get(self, request, *args, **kwargs):
        if self.get_object().patient is None:
            messages.info(request, "You need to book an appointment to access this page")
            return redirect(
                reverse_lazy('connect_therapy:book-appointment', kwargs={'pk': self.get_object().practitioner.user_id}))
        return super().get(self, request, *args, **kwargs)

    def test_func(self):
        # if the patient id for the appointment is None, we will let it pass, but redirect in the get method above
        if self.get_object().patient is None:
            return True
        return (self.request.user.id == self.get_object().patient.user.id) \
               or (self.request.user.id == self.get_object().practitioner.user.id)


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


class PractitionerSignUpView(FormView):
    form_class = PractitionerSignUpForm
    template_name = 'connect_therapy/practitioner/signup.html'
    success_url = reverse_lazy('connect_therapy:practitioner-signup-success')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.username = user.email
        user.save()
        practitioner = Practitioner(
            user=user,
            address_line_1=form.cleaned_data['address_line_1'],
            address_line_2=form.cleaned_data['address_line_2'],
            postcode=form.cleaned_data['postcode'],
            mobile=form.cleaned_data['mobile'],
            bio=form.cleaned_data['bio']
        )
        practitioner.save()
        user = authenticate(username=form.cleaned_data['email'],
                            password=form.cleaned_data['password1']
                            )
        login(request=self.request, user=user)
        return super().form_valid(form)


class PractitionerLoginView(auth_views.LoginView):
    template_name = 'connect_therapy/practitioner/login.html'
    authentication_form = PractitionerLoginForm

    def get_success_url(self):
        return reverse_lazy('connect_therapy:practitioner-login-success')


class PractitionerNotesView(FormView):
    form_class = PractitionerNotesForm
    template_name = 'connect_therapy/practitioner/notes.html'
    success_url = reverse_lazy('connect_therapy:practitioner-login-success')

    def form_valid(self, form):
        self.appointment.practitioner_notes = form.cleaned_data['practitioner_notes']
        self.appointment.patient_notes_by_practitioner = form.cleaned_data['patient_notes_by_practitioner']
        self.appointment.save()
        return super().form_valid(form)

    def get(self, request, appointment_id):
        self.appointment = get_object_or_404(Appointment, pk=appointment_id)
        return super().get(request)

    def post(self, request, appointment_id):
        self.appointment = get_object_or_404(Appointment, pk=appointment_id)
        return super().post(request)


class PractitionerMyAppointmentsView(generic.TemplateView):
    template_name = 'connect_therapy/practitioner/my-appointments.html'

    model = Appointment

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['future_appointments'] = Appointment.objects.filter(
            start_date_and_time__gte=timezone.now(),
            practitioner=self.request.user.practitioner
        ).order_by('-start_date_and_time')
        context['past_appointments'] = Appointment.objects.filter(
            start_date_and_time__lt=timezone.now(),
            practitioner=self.request.user.practitioner
        ).order_by('-start_date_and_time')
        return context


class ViewBookableAppointments(UserPassesTestMixin, DetailView):
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


class ReviewSelectedAppointments(UserPassesTestMixin, TemplateView):
    template_name = 'connect_therapy/patient/bookings/review-selection.html'
    login_url = reverse_lazy('connect_therapy:patient-login')
    patient = Patient()

    def test_func(self):
        if self.request.user.is_anonymous:
            return False
        try:
            patient = Patient.objects.get(user=self.request.user)
            return True
        except Patient.DoesNotExist:
            return False

    def post(self, request, *args, **kwargs):
        app_ids = request.POST.getlist('app_id')
        practitioner_id = kwargs['pk']

        if len(app_ids) == 0:
            messages.warning(request, "You haven't selected any appointments")
            return ViewBookableAppointments.get(self, request, practitioner_id)

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
                request.session['bookable_appointments'] = self._appointments_to_dictionary_list(bookable_appointments)
                request.session['merged_appointments'] = self._appointments_to_dictionary_list(merged_appointments)
                request.session['patient_id'] = self.patient.id
                return render(request, self.get_template_names(), {"bookable_appointments": bookable_appointments,
                                                                   "merged_appointments": merged_appointments,
                                                                   "practitioner_id": practitioner_id})
        else:
            # appointments not valid
            invalid_appointments = True
            return render(request, self.get_template_names(), context={"invalid_appointments": invalid_appointments})

    @staticmethod
    def _appointments_to_dictionary_list(appointments):
        dict_list = []
        for app in appointments:
            appointment_dict = {'id': app.id, 'practitioner_id': app.practitioner.id,
                                'start_date_and_time': str(app.start_date_and_time), 'length': str(app.length),
                                'session_id': str(app.session_id), 'session_salt': str(app.session_salt)}
            dict_list.append(appointment_dict)
        return dict_list


class Checkout(UserPassesTestMixin, TemplateView):
    login_url = reverse_lazy('connect_therapy:patient-login')
    template_name = "connect_therapy/patient/bookings/checkout.html"
    patient = Patient()

    def test_func(self):
        if self.request.user.is_anonymous:
            return False
        try:
            patient = Patient.objects.get(user=self.request.user)
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
                return render(request, "connect_therapy/patient/bookings/booking-success.html", {})
            else:
                return HttpResponse("Failed to book. Patient object doesnt exist.")


class PatientCancelAppointmentView(FormMixin, DetailView):
    model = Appointment
    form_class = forms.Form
    template_name = 'connect_therapy/appointment_detail.html'

    def get_success_url(self):
        return reverse_lazy('connect_therapy:patient-my-appointments')

    def get_context_data(self, **kwargs):
        context = super(PatientCancelAppointmentView, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def form_valid(self, form):
        # Here, we would record the user's interest using the message
        # passed in form.cleaned_data['message']
        self.object.patient = None
        self.object.save()

        return super(PatientCancelAppointmentView, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class PractitionerPreviousNotesView(LoginRequiredMixin, generic.DetailView):
    login_url = reverse_lazy('connect_therapy:practitioner-appointment-notes')
    model = Appointment
    template_name = 'connect_therapy/practitioner/appointment-notes.html'


class PractitionerCurrentNotesView(LoginRequiredMixin, generic.DetailView):
    login_url = reverse_lazy('connect_therapy:practitioner-before-meeting-notes')
    model = Appointment
    template_name = 'connect_therapy/practitioner/before-meeting-notes.html'


class PatientPreviousNotesView(LoginRequiredMixin, generic.DetailView):
    login_url = reverse_lazy('connect_therapy:patient-appointment-notes')
    model = Appointment
    template_name = 'connect_therapy/patient/appointment-notes.html'
