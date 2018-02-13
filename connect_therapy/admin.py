from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin as UserAdminParent

from connect_therapy.models import Practitioner


def mark_approved(modeladmin, request, queryset):
    queryset.update(is_approved=True)


mark_approved.short_description = "Mark as approved"


def mark_not_approved(modeladmin, request, queryset):
    queryset.update(is_approved=False)


mark_not_approved.short_description = "Mark as not approved"


@admin.register(Practitioner)
class PractitionerAdmin(admin.ModelAdmin):
    first_name = lambda x: x.user.first_name
    first_name.short_description = "First Name"
    last_name = lambda x: x.user.last_name
    last_name.short_description = "Last Name"
    email = lambda x: x.user.email
    email.short_description = "Email"
    list_display = (first_name, last_name, email, 'is_approved')
    list_filter = ('is_approved',)
    actions = (mark_approved, mark_not_approved)
    search_fields = ('user__first_name', 'user__last_name', 'user__email')


admin.site.unregister(Group)
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(UserAdminParent):
    def has_module_permission(self, request):
        """This stops the UserAdmin appearing on the home page"""
        return False
