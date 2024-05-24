from django.contrib import admin
from .models import Department, Employee, Role, Task, Project, Ticket


def get_current(request):
    user = Employee.objects.get(Employee= request.user)
    return user

# Register your models here.
class TaskAdmin(admin.ModelAdmin):
    # exclude = ['task_assigned_by']
    def save_model(self, request, obj, form, change):
        if not obj.task_assigned_by:
            obj.task_assigned_by = get_current(request)
        obj.save()

class TicketAdmin(admin.ModelAdmin):
    # exclude = ['ticket_assigned_by']
    def save_model(self, request, obj, form, change):
        if not obj.ticket_assigned_by:
            obj.ticket_assigned_by = get_current(request)
        obj.save()

admin.site.register(Employee)
admin.site.register(Department)
admin.site.register(Role)
admin.site.register(Project)
# admin.site.register(Team)
admin.site.register(Task, TaskAdmin)
admin.site.register(Ticket, TicketAdmin)