from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView, DetailView, UpdateView
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views import generic
from django.forms.formsets import formset_factory

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

    def test_func(self):
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


class PatientEditDetails(UpdateView):
    model = User
    form_class = PatientEditDetailsForm
    success_url = reverse_lazy('connect_therapy:patient-signup-success')
    template_name = 'connect_therapy/patient/edit-details.html'

    def edit_profile(self, request):
        user = request.user
        form = PatientEditDetailsForm(request.POST, instance=request.user)
        if request.method == 'POST':
            if form.is_valid():
                form.save()
        else:
            form = PatientEditDetailsForm

            # return HttpResponse

        context = {'form': form}
        return render(request, 'connect_therapy/patient/edit-details.html',
                      context)


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
