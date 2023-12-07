from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название отдела")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Отдел"
        verbose_name_plural = "Отделы"


class Employee(models.Model):
    surname = models.CharField(max_length=100, null=True, verbose_name="Фамилия")
    name = models.CharField(max_length=100, null=True, verbose_name="Имя")
    patronymic = models.CharField(max_length=100, null=True, verbose_name="Отчество")
    position = models.CharField(max_length=100, null=True, verbose_name="Должность")
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name="Зарплата")
    login = models.CharField(max_length=50, verbose_name="Логин")
    email = models.EmailField(unique=True, null=True, verbose_name="Email")
    password = models.CharField(max_length=255, verbose_name="Пароль")
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Отдел")
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=1, null=True, verbose_name="Рейтинг")
    max_tasks_limit = models.PositiveIntegerField(default=5, null=True, verbose_name="Лимит задач")
    is_blocked = models.BooleanField(default=False, verbose_name="Заблокирован")

    def __str__(self):
        return f"{self.surname} {self.name} ({self.login})"

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"


class Task(models.Model):
    DIFFICULTY_CHOICES = [
        (1, 'Очень легкая'),
        (2, 'Легкая'),
        (3, 'Средняя'),
        (4, 'Трудная'),
        (5, 'Очень трудная'),
    ]
    title = models.CharField(max_length=255, verbose_name="Название")
    deadline = models.DateField(verbose_name="Срок выполнения")
    status = models.CharField(max_length=50, default="Свободна", verbose_name="Статус")
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, default=1, verbose_name="Сложность")
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Отдел")
    notifications_sent = models.IntegerField(default=0, verbose_name="Отправленные уведомления")

    def __str__(self):
        return f"{self.title} | {self.difficulty} | {self.status}"

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"


class TaskAssignment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name="Задача")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, verbose_name="Сотрудник")
    is_completed = models.BooleanField(default=False, verbose_name="Завершено")

    def __str__(self):
        return f"{self.employee} - {self.task}"

    class Meta:
        verbose_name = "Назначение задачи"
        verbose_name_plural = "Назначения задач"


class Notes(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Сотрудник")
    date = models.DateField(null=True, verbose_name="Дата")
    note = models.TextField(verbose_name="Примечание")

    def __str__(self):
        return f"{self.employee} - {self.date}"

    class Meta:
        verbose_name = "Напоминание"
        verbose_name_plural = "Напоминания"


def get_tasks_for_employee(self):
    return TaskAssignment.objects.filter(employee=self).values('task__title', 'task__deadline', 'task__status')


class TaskRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Сотрудник")
    task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Задача")


def request_task(self, task):
    task_request = TaskRequest(employee=self, task=task)
    task_request.save()


class EmployeeRating(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, verbose_name="Сотрудник")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name="Рейтинг")
    is_blocked = models.BooleanField(default=False, verbose_name="Заблокирован")

    def __str__(self):
        return f"{self.employee} {self.rating} ({self.is_blocked})"

    class Meta:
        verbose_name = "Рейтинг сотрудника"
        verbose_name_plural = "Рейтинги сотрудников"


class Issue(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name="Задача")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Сотрудник")
    status = models.TextField(verbose_name="Статус")

    class Meta:
        verbose_name = "Проблема"
        verbose_name_plural = "Проблемы"


def can_take_task(self):
    current_task_count = TaskAssignment.objects.filter(employee=self, is_completed=False).count()
    return current_task_count < self.max_tasks_limit


class EmployeeConfirmation(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, verbose_name="Сотрудник")
    is_confirmed = models.BooleanField(default=False, verbose_name="Подтвержден")

    def __str__(self):
        return f"{self.employee} - {'Подтвержден' if self.is_confirmed else 'Не подтвержден'}"

    class Meta:
        verbose_name = "Подтверждение сотрудника"
        verbose_name_plural = "Подтверждения сотрудников"
