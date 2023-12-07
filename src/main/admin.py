from django.contrib import admin
from .models import Employee, Task, TaskAssignment, EmployeeRating, Issue, Department, EmployeeConfirmation, Notes

admin.site.register(Employee)
admin.site.register(Task)
admin.site.register(TaskAssignment)
admin.site.register(EmployeeRating)
admin.site.register(Issue)
admin.site.register(Department)
admin.site.register(EmployeeConfirmation)
admin.site.register(Notes)
