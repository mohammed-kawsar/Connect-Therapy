from django.core.management import BaseCommand

from connect_therapy import notifications


class Command(BaseCommand):
    def handle(self, *args, **options):
        notifications.reminders()
