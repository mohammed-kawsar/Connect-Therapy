from django import forms
from django.contrib.auth import authenticate, login, views as auth_views
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic
from django.views.generic import FormView, DetailView
from django.views.generic.edit import FormMixin

from connect_therapy.forms.patient import PatientSignUpForm, PatientLoginForm,\
    PatientNotesBeforeForm
from connect_therapy.models import Patient, Appointment


class PatientSignUpView(FormView):
    form_class = PatientSignUpForm
    template_name = 'connect_therapy/patient/signup.html'
    success_url = reverse_lazy('connect_therapy:patient-login')

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
        return reverse_lazy('connect_therapy:patient-homepage')


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


class PatientNotesBeforeView(FormMixin, UserPassesTestMixin, DetailView):
    form_class = PatientNotesBeforeForm
    template_name = 'connect_therapy/patient/notes-before-appointment.html'
    success_url = reverse_lazy('connect_therapy:patient-my-appointments')
    login_url = reverse_lazy('connect_therapy:patient-my-appointments')
    redirect_field_name = None
    model = Appointment

    def test_func(self):
        return self.request.user.id == self.get_object().patient.user.id

    def form_valid(self, form):
        self.appointment.patient_notes_before_meeting = \
            form.cleaned_data['patient_notes_before_meeting']
        self.appointment.save()
        return super().form_valid(form)

    def post(self, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid()
        else:
            return self.form_invalid()


class PatientCancelAppointmentView(UserPassesTestMixin, FormMixin, DetailView):
    model = Appointment
    form_class = forms.Form
    template_name = 'connect_therapy/appointment_detail.html'
    login_url = reverse_lazy('connect_therapy:patient-my-appointments')
    redirect_field_name = None

    def test_func(self):
        return self.request.user.id == self.get_object().patient.user.id

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


class PatientPreviousNotesView(UserPassesTestMixin, generic.DetailView):
    login_url = reverse_lazy('connect_therapy:patient-my-appointments')
    redirect_field_name = None
    model = Appointment
    template_name = 'connect_therapy/patient/appointment-notes.html'

    def test_func(self):
        return self.request.user.id == self.get_object().patient.user.id
