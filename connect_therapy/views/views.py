from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import DetailView

from connect_therapy.forms.forms import FileForm
from connect_therapy.models import Appointment


class ChatView(UserPassesTestMixin, DetailView):
    model = Appointment
    template_name = 'connect_therapy/chat.html'
    login_url = reverse_lazy('connect_therapy:patient-login')

    def get(self, request, *args, **kwargs):
        form = FileForm()
        super().get(request, *args, **kwargs)
        return render(request, self.get_template_names(), {"upload_form": form,
                                                           "object": self.get_object()})

    def test_func(self):
        return (self.request.user.id == self.get_object().patient.user.id) \
               or (self.request.user.id == self.get_object().practitioner.user.id)


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
