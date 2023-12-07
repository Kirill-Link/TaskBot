# main/admin.py

from django.contrib import admin
from .models import Employee, Task, TaskAssignment

admin.site.register(Employee)
admin.site.register(Task)
admin.site.register(TaskAssignment)
