from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from .models import MailTemplate, Employee, Department, JobRole

# Register simple models
admin.site.register(Employee)
admin.site.register(Department)
admin.site.register(JobRole)

# Register MailTemplate safely
class MailTemplateAdmin(admin.ModelAdmin):
    list_display = ('key', 'title', 'updated_at')
    search_fields = ('key', 'title', 'subject')
    readonly_fields = ('updated_at',)

try:
    admin.site.register(MailTemplate, MailTemplateAdmin)
except AlreadyRegistered:
    pass
