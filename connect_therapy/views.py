from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic
from django.views.generic import FormView, DetailView
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
        upload_form = FileForm
        return render(request, self.get_template_names(), {"upload_form": upload_form,
                                                           "object": self.get_object()})

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


class PatientNotesBeforeView(LoginRequiredMixin, FormView):
    form_class = PatientNotesBeforeForm
    template_name = 'connect_therapy/patient/notes-before-appointment.html'
    success_url = reverse_lazy('connect_therapy:patient-my-appointments')

    def form_valid(self, form):
        self.appointment.patient_notes_before_meeting = \
            form.cleaned_data['patient_notes_before_meeting']
        self.appointment.save()
        return super().form_valid(form)

    def get(self, request, appointment_id):
        self.appointment = get_object_or_404(Appointment, pk=appointment_id)
        return super.get(request)

    def post(self, request, appointment_id):
        self.appointment = get_object_or_404(Appointment, pk=appointment_id)
        return super().post(request)


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


class FileUploadView(LoginRequiredMixin, generic.DetailView):
    login_url = reverse_lazy('connect_therapy:patient-login')
    template_name = "connect_therapy/file_transfer/file_upload.html"
    model = Appointment

    def get(self, request, *args, **kwargs):
        form = FileForm()
        super().get(request, *args, **kwargs)
        return render(request, self.get_template_names(), {"form": form})

    def post(self, request, *args, **kwargs):
        form = FileForm(request.POST, request.FILES)
        self.object = self.get_object()
        if form.is_valid():
            import boto3
            s3 = boto3.resource("s3")
            name = str(form.cleaned_data['file_name'])
            file = form.cleaned_data['file']

            """ TODO: check if file name already exists, will do once i intergrate this view with a detail view for 
            appointment as I intend to put files for an appointment within a separate directory
            """

            s3.meta.client.put_object(Body=file,
                                      Bucket='segwyn',
                                      Key=str(self.object.id) + "/" + str(name), ContentType=file.content_type)

            s3.meta.client.put_object_tagging(
                Bucket='segwyn',
                Key=str(self.object.id) + "/" + str(name),
                Tagging={
                    'TagSet': [
                        {
                            'Key': 'Uploader_user_id',
                            'Value': str(request.user.id)
                        },
                        {
                            'Key': 'Appointment_ID',
                            'Value': str(self.object.id)
                        },
                    ]
                }
            )

            return HttpResponse("Uploading " + form.cleaned_data['file_name'])

        return HttpResponse("Failed to upload the file")


class FileDownloadView(generic.TemplateView):
    template_name = "connect_therapy/file_transfer/file_download.html"

    def get(self, request, *args, **kwargs):
        form = FileForm()
        import boto3
        s3 = boto3.resource("s3")
        bucket = s3.Bucket("segwyn")
        files = []

        files.append(self.get_files_from_folder("someFile"))

        super().get(request, *args, **kwargs)

        return render(request, self.get_template_names(), {"files": files})

    def get_files_from_folder(self, folder_name):
        import boto3
        s3 = boto3.resource("s3")
        bucket = s3.Bucket("segwyn")
        files = []
        prefix = folder_name + "/"
        file_not_found = True
        for obj in bucket.objects.filter(Prefix=prefix):
            file_not_found = False
            files.append(obj.key)

        if file_not_found:
            print("ALERT", "No file in {0}/{1}".format(bucket, prefix))

        return files

    def generate_presigned_url(self, keys):
        import boto3
        urls = []
        for key in keys:
            url = boto3.client('s3', config=boto3.session.Config(signature_version='s3v4',
                                                                 region_name='eu-west-2')).generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': 'segwyn',
                    'Key': key
                },
                ExpiresIn=900
            )
            urls.append(str(url))

        return urls

    def get_objects_with_tag(self, uploader_user_id, appointment_id):
        import boto3
        s3 = boto3.resource("s3")
        bucket = s3.Bucket("segwyn")
        files = []
        if len(uploader_user_id) > 0:
            files.append(self._get_objects_with_key_value(bucket.objects.all(), "Uploader", uploader_user_id))
        if len(appointment_id) > 0:
            files.append(self._get_objects_with_key_value(bucket.objects.all(), "Appointment_ID", appointment_id))

        return files

    def _get_objects_with_key_value(self, objects, key, value):
        import boto3
        s3 = boto3.resource("s3")

        files = []
        for obj in objects:
            tag_set = s3.meta.client.get_object_tagging(Bucket="segwyn",
                                                        Key=obj.key)['TagSet']

            if len(tag_set) > 0:
                for x in range(0, len(tag_set)):
                    if tag_set[x]['Key'] == str(key) and tag_set[x]['Value'] == str(value):
                        files.append(obj.key)

        return files
