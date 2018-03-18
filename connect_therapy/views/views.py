from django.contrib.auth import login
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views import generic
from django.views.generic import DetailView

from connect_therapy.forms.forms import FileForm
from connect_therapy.models import Appointment, Patient, Practitioner
from connect_therapy.tokens import account_activation_token


class ChatView(UserPassesTestMixin, DetailView):
    model = Appointment
    template_name = 'connect_therapy/chat.html'
    login_url = reverse_lazy('connect_therapy:patient-login')

    def get(self, request, *args, **kwargs):
        files_for_appointment = FileDownloadView.get_files_from_folder(self, str(self.get_object().id))
        downloadable_file_list = FileDownloadView.generate_pre_signed_url_for_each(self,files_for_appointment)

        form = FileForm()
        
        if self.get_object().patient is None:
            messages.info(request, "You should book an appointment to access this page")
            return redirect(reverse_lazy('connect_therapy:book-appointment',
                                         kwargs={'pk': self.get_object().practitioner.id}))

        super().get(request, *args, **kwargs)
        return render(request, self.get_template_names(), {"upload_form": form,
                                                           "object": self.get_object(),
                                                           "downloadable_files": downloadable_file_list})

    def test_func(self):
        # if the patient is empty, we will let the user pass only to redirect them to the book appointment page
        # for this appointment in the get method above
        if self.get_object().patient is None:
            return True
        if self.request.user.id == self.get_object().patient.user.id:
            return self.get_object().patient.email_confirmed
        elif self.request.user.id == self.get_object().practitioner.user.id:
            return self.get_object().practitioner.email_confirmed


class FileUploadView(LoginRequiredMixin, generic.DetailView):
    login_url = reverse_lazy('connect_therapy:patient-login')
    template_name = "connect_therapy/file_transfer/file_upload.html"
    model = Appointment

    def get(self, request, *args, **kwargs):
        form = FileForm()
        super().get(request, *args, **kwargs)
        return render(request, self.get_template_names(), {"upload_form": form})

    def post(self, request, *args, **kwargs):
        form = FileForm(request.POST, request.FILES)
        self.object = self.get_object()
        is_valid = False
        uploaded_file = ()
        if form.is_valid():
            print("called once")
            import boto3
            s3 = boto3.resource("s3")
            file = form.cleaned_data['file']

            """ TODO: check if file name already exists, will do once i intergrate this view with a detail view for 
            appointment as I intend to put files for an appointment within a separate directory
            """
            # push to S3
            key = str(self.object.id) + "/" + str(file.name)
            s3.meta.client.put_object(Body=file,
                                      Bucket='segwyn',
                                      Key=key, ContentType=file.content_type)

            # add tags to file in s3
            s3.meta.client.put_object_tagging(
                Bucket='segwyn',
                Key=str(self.object.id) + "/" + str(file.name),
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

            # get file to return to view

            uploaded_file = (key.split('/')[1], FileDownloadView.generate_presigned_url(self, key))

            is_valid = True

        return JsonResponse({'is_valid': is_valid, 'uploaded_files': uploaded_file})



class FileDownloadView(DetailView):
    model = Appointment

    def get(self, request, *args, **kwargs):
        form = FileForm()
        import boto3
        s3 = boto3.resource("s3")
        bucket = s3.Bucket("segwyn")
        files = {}
        self.object = self.get_object()

        for file in self.get_files_from_folder(str(self.object.id)):
            files[file] = self._generate_presigned_url(file)

        return JsonResponse({'downloadable_files': files})

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

    def generate_pre_signed_url_for_each(self, files):
        downloadable_file_list = []
        for file in files:
            downloadable_file_list.append(
                [file.split("/")[1], FileDownloadView._generate_presigned_url(self, file)]
            )
        return downloadable_file_list

    def _generate_presigned_url(self, key):
        import boto3
        url = boto3.client('s3', config=boto3.session.Config(signature_version='s3v4',
                                                             region_name='eu-west-2')).generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': 'segwyn',
                'Key': key
            },
            ExpiresIn=1800
        )
        return str(url)

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


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        login(request, user)
        try:
            patient = user.patient
            patient.email_confirmed = True
            patient.save()
            return redirect('connect_therapy:patient-homepage')
        except Patient.DoesNotExist:
            pass
        try:
            practitioner = user.practitioner
            practitioner.email_confirmed = True
            practitioner.save()
            return redirect('connect_therapy:practitioner-homepage')
        except Practitioner.DoesNotExist:
            pass
        return redirect('connect_therapy:index')
    else:
        return redirect('connect_therapy:index')