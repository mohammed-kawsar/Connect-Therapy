from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin as UserAdminParent

from connect_therapy.models import Practitioner, Patient, Appointment


@admin.register(Practitioner)
class PractitionerAdmin(admin.ModelAdmin):
    def get_user_first_name(practitioner):
        return practitioner.user.first_name

    def get_user_last_name(practitioner):
        return practitioner.user.last_name

    def get_user_email(practitioner):
        return practitioner.user.email

    def mark_approved(modeladmin, request, queryset):
        queryset.update(is_approved=True)

    def mark_not_approved(modeladmin, request, queryset):
        queryset.update(is_approved=False)

    get_user_first_name.short_description = "First Name"
    get_user_last_name.short_description = "Last Name"
    get_user_email.short_description = "Email"
    mark_approved.short_description = "Mark as approved"
    mark_not_approved.short_description = "Mark as not approved"
    list_display = (get_user_first_name,
                    get_user_last_name,
                    get_user_email, 'is_approved'
                    )
    list_filter = ('is_approved',)
    actions = (mark_approved, mark_not_approved)
    search_fields = ('user__first_name', 'user__last_name', 'user__email')


admin.site.unregister(Group)
admin.site.unregister(User)

admin.site.site_header = 'Connect Therapy Administration'
admin.site.site_title = 'Connect Therapy - Admin'


@admin.register(User)
class UserAdmin(UserAdminParent):
    def has_module_permission(self, request):
        """This stops the UserAdmin appearing on the home page"""
        return False
