from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView, DetailView, UpdateView, TemplateView
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views import generic
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormMixin
from django import forms

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


class PatientProfile(LoginRequiredMixin, generic.TemplateView):
    template_name = 'connect_therapy/patient/profile.html'

    @login_required
    def view_profile(self, request):
        user = request.user
        args = {'user': user}
        return render(request, args)


class PatientEditDetails(UpdateView):
    model = Patient
    template_name = 'connect_therapy/patient/edit-profile.html'
    form_class = PatientUserForm
    second_form_class = PatientForm
    success_url = reverse_lazy('connect_therapy:patient-profile')

    def get_context_data(self, **kwargs):
        context = super(PatientEditDetails, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        context['patient'] = self.request.user.patient
        if 'form' not in context:
            context['form'] = self.form_class(self.request.GET,
                                              instance=self.request.user)
        if 'form2' not in context:
            context['form2'] = self.second_form_class(self.request.GET,
                                                      instance=self.request.user.patient)
        return context

    def get(self, request, *args, **kwargs):
        super(PatientEditDetails, self).get(request, *args, **kwargs)
        form = self.form_class
        form2 = self.second_form_class
        return self.render_to_response(self.get_context_data(
            object=self.object, form=form, form2=form2))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST)
        form2 = self.second_form_class(request.POST)

        if form.is_valid() and form2.is_valid():
            user_data = form.save(commit=False)
            user_data.save()
            user_data.username = user_data.email
            user_data.save()
            patient_data = form2.save(commit=False)
            patient_data.user = user_data
            patient_data.save()
        else:
            return self.render_to_response(
                self.get_context_data(form=form, form2=form2))


class PatientEditDetailsView(LoginRequiredMixin, UpdateView):
    model = Patient
    form_class = PatientEditDetailsForm
    success_url = reverse_lazy('connect_therapy:patient-profile')
    template_name = 'connect_therapy/patient/edit-profile.html'

    # Returns the object to populate the form and to update the model.
    # Issue here is can only do either user or patient not both.
    def get_object(self, queryset=None):
        return self.request.user.patient

    # Ensures only logged in user can edit their profile and posts the
    # form to update the model.
    @login_required
    def edit_profile(self, request):
        user = request.user.patient
        form = PatientEditDetailsForm(request.POST,
                                      instance=user)
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                user.username = user.email
                user.save()
        else:
            form = PatientEditDetailsForm

        context = {'form': form}
        return render(request, 'connect_therapy/patient/edit-profile.html',
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
