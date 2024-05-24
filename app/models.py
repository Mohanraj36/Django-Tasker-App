from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from  datetime import datetime

# Create your models here.

class Department(models.Model):
    department_id = models.CharField(max_length=50)
    department_name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f'Department ID: {self.department_id} | Department Name: {self.department_name}'

class Role(models.Model):
    role_id = models.CharField(max_length=50)
    role_name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f'Role ID: {self.role_id} Role Name: {self.role_name}'

class Employee(models.Model):
    Employee = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.Employee}'


class Project(models.Model):
    status = {
        "Open": "Open",
        "In Progress": "In Progress",
        "Completed": "Completed"
    }
    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=50)
    project_description = models.TextField(max_length=255)
    project_client_name = models.CharField(max_length=50)
    project_client_email = models.EmailField()
    project_lead = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='Project_Lead')
    project_members = models.ManyToManyField(Employee, related_name='Project_Members')
    
    project_status = models.CharField(max_length=20, choices=status)
    

    def __str__(self) -> str:
        return f'{self.project_name}'

class Task(models.Model):

    priority = {
        "High": "High",
        "Medium": "Medium",
        "Low": "Low"
    }
    status = {
        "Open": "Open",
        "In Progress": "In Progress",
        "Completed": "Completed"
    }

    task_id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    task_name = models.CharField(max_length=50)
    task_description = models.TextField(max_length=255)
    task_assigned_by = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, null=True, blank=True, editable=False)
    task_assigned_to = models.ManyToManyField(Employee, related_name='task_assigned_to')
    task_priority = models.CharField(max_length=10, choices=priority)
    task_status = models.CharField(max_length=20, choices=status)
    task_due_date = models.DateTimeField()
    task_created_at = models.DateTimeField(auto_now_add=True)
    task_completed_at = models.DateTimeField(auto_now=True,null=True, blank=True)

    def __str__(self) -> str:
        assigned_employees = ', '.join(str(employee) for employee in self.task_assigned_to.all())
        return f'Task ID: {self.task_id} From: {self.task_assigned_by} | Assigned To: {assigned_employees} | Status: {self.task_status} | Priority: {self.task_priority} {self.task_completed_at}'

class Ticket(models.Model):

    status = {
        "Open": "Open",
        "In Progress": "In Progress",
        "Completed": "Completed"
    }

    priority = {
        "High": "High",
        "Medium": "Medium",
        "Low": "Low"
    }

    ticket_id = models.AutoField(primary_key=True)
    ticket_name = models.CharField(max_length=50)
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING)
    ticket_assigned_by = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, null=True, blank=True, editable=False)
    ticket_description = models.TextField(max_length=512)
    ticket_priority = models.CharField(max_length=10, choices=priority)
    ticket_status = models.CharField(max_length=20, choices=status)
    ticket_assigned_to = models.ManyToManyField(Employee, related_name='ticket_assigned_to')
    ticket_due_date = models.DateTimeField()
    ticket_raised_by_client = models.BooleanField(default=False)
    ticket_created_at = models.DateTimeField(auto_now_add=True)
    ticket_completed_at = models.DateTimeField(auto_now=True,null=True, blank=True)
    
    def __str__(self) -> str:
        assigned_employees = ', '.join(str(employee) for employee in self.ticket_assigned_to.all())
        # {datetime.datetime.strftime(self.ticket_completed_at,"%m/%d/%Y, %H:%M:%S")
        return f'Ticket ID: {self.ticket_id} | Project Name: {self.project} | From: {self.ticket_assigned_by} | To: {assigned_employees}'

