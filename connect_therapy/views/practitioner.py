import re

from django.contrib.auth import authenticate, login, update_session_auth_hash, views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic
from django.views.generic import FormView, UpdateView, DeleteView

from connect_therapy import notifications
from connect_therapy.forms.practitioner import PractitionerSignUpForm, PractitionerLoginForm, \
    PractitionerNotesForm, PractitionerEditMultiForm, PractitionerDefineAppointmentForm
from connect_therapy.models import Practitioner, Appointment


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
        ).order_by('start_date_and_time')
        context['past_appointments'] = Appointment.objects.filter(
            start_date_and_time__lt=timezone.now(),
            practitioner=self.request.user.practitioner
        ).order_by('start_date_and_time')
        return context


class PractitionerPreviousNotesView(LoginRequiredMixin, generic.DetailView):
    login_url = reverse_lazy('connect_therapy:practitioner-appointment-notes')
    model = Appointment
    template_name = 'connect_therapy/practitioner/appointment-notes.html'


class PractitionerCurrentNotesView(LoginRequiredMixin, generic.DetailView):
    login_url = reverse_lazy('connect_therapy:practitioner-before-meeting-notes')
    model = Appointment
    template_name = 'connect_therapy/practitioner/before-meeting-notes.html'


class PractitionerAllPatientsView(generic.TemplateView):
    template_name = 'connect_therapy/practitioner/view-patients.html'
    model = Appointment

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointments = Appointment.objects.filter(
            practitioner=self.request.user.practitioner
        ).order_by('-start_date_and_time')
        patients_already_seen = []
        appointments_unique_patient = []
        for appointment in appointments:
            if appointment.patient not in patients_already_seen:
                appointments_unique_patient.append(appointment)
                patients_already_seen.append(appointment.patient)
        context['appointments'] = appointments_unique_patient
        return context


class PractitionerProfile(LoginRequiredMixin, generic.TemplateView):
    template_name = 'connect_therapy/practitioner/profile.html'

    @login_required
    def view_profile(self, request):
        user = request.user
        args = {'user': user}
        return render(request, args)


class PractitionerEditDetailsView(UpdateView):
    model = Practitioner
    template_name = 'connect_therapy/practitioner/edit-profile.html'
    form_class = PractitionerEditMultiForm
    success_url = reverse_lazy('connect_therapy:practitioner-profile')

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
            if form.is_valid():
                return self.form_valid(form)

        return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super(PractitionerEditDetailsView, self).get_form_kwargs()
        kwargs.update(instance={
            'user': self.object.user,
            'practitioner': self.object,
        })
        return kwargs


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect(reverse_lazy('connect_therapy:practitioner-profile'))
        else:
            return redirect(reverse_lazy('connect_therapy:practitioner-change-password'))
    else:
        form = PasswordChangeForm(user=request.user)
        args = {'form': form}
        return render(request, 'connect_therapy/practitioner/change-password.html', args)


class PractitionerSetAppointmentView(LoginRequiredMixin, FormView):
    login_url = reverse_lazy('connect_therapy:practitioner-login')
    form_class = PractitionerDefineAppointmentForm
    template_name = 'connect_therapy/practitioner/set-appointment-page.html'
    success_url = reverse_lazy('connect_therapy:practitioner-my-appointments')

    def form_valid(self, form):
        appointment = Appointment(
            patient=None,
            practitioner=self.request.user.practitioner,
            start_date_and_time=form.cleaned_data['start_date_and_time'],
            length=form.cleaned_data['length']
        )

        over_lap_free, over_laps = Appointment.get_appointment__practitioner_overlaps(appointment,
                                                                                      self.request.user.practitioner)
        if not over_lap_free:
            over_laps_str = re.sub("<|>|\[\[|\]\]", "", str(over_laps))
            over_laps_str = over_laps_str.replace(",", " and ")
            return render(self.request, 'connect_therapy/practitioner/appointment-overlap.html',
                          context={"overlaps": over_laps_str})
        else:
            appointment.save()
            return super().form_valid(form)


class PractitionerAppointmentDelete(DeleteView):
    model = Appointment
    template_name = 'connect_therapy/practitioner/appointment-cancel.html'
    fields = ['practitioner', 'patient', 'start_date_and_time', 'length', 'practitioner_notes',
              'patient_notes_by_practitioner']
    success_url = reverse_lazy('connect_therapy:practitioner-my-appointments')

    def delete(self, request, *args, **kwargs):
        message = request.POST['cancel-message']
        self.object = self.get_object()
        notifications.appointment_cancelled_by_practitioner(self.object, message)
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)
