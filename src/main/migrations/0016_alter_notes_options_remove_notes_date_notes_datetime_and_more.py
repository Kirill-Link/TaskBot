# Generated by Django 4.2.7 on 2023-11-22 18:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_notes'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notes',
            options={'verbose_name': 'Напоминание', 'verbose_name_plural': 'Напоминания'},
        ),
        migrations.RemoveField(
            model_name='notes',
            name='date',
        ),
        migrations.AddField(
            model_name='notes',
            name='datetime',
            field=models.DateTimeField(null=True, verbose_name='Дата и время'),
        ),
        migrations.AlterField(
            model_name='department',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Название отдела'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.department', verbose_name='Отдел'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='email',
            field=models.EmailField(max_length=254, null=True, unique=True, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='login',
            field=models.CharField(max_length=50, verbose_name='Логин'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='max_tasks_limit',
            field=models.PositiveIntegerField(default=5, null=True, verbose_name='Лимит задач'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='name',
            field=models.CharField(max_length=100, null=True, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='password',
            field=models.CharField(max_length=255, verbose_name='Пароль'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='patronymic',
            field=models.CharField(max_length=100, null=True, verbose_name='Отчество'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='position',
            field=models.CharField(max_length=100, null=True, verbose_name='Должность'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='rating',
            field=models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=1, null=True, verbose_name='Рейтинг'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='salary',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True, verbose_name='Зарплата'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='surname',
            field=models.CharField(max_length=100, null=True, verbose_name='Фамилия'),
        ),
        migrations.AlterField(
            model_name='employeeconfirmation',
            name='employee',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='main.employee', verbose_name='Сотрудник'),
        ),
        migrations.AlterField(
            model_name='employeeconfirmation',
            name='is_confirmed',
            field=models.BooleanField(default=False, verbose_name='Подтвержден'),
        ),
        migrations.AlterField(
            model_name='employeerating',
            name='employee',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='main.employee', verbose_name='Сотрудник'),
        ),
        migrations.AlterField(
            model_name='employeerating',
            name='is_blocked',
            field=models.BooleanField(default=False, verbose_name='Заблокирован'),
        ),
        migrations.AlterField(
            model_name='employeerating',
            name='rating',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=3, verbose_name='Рейтинг'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.employee', verbose_name='Сотрудник'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='status',
            field=models.TextField(verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.task', verbose_name='Задача'),
        ),
        migrations.AlterField(
            model_name='notes',
            name='employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.employee', verbose_name='Сотрудник'),
        ),
        migrations.AlterField(
            model_name='notes',
            name='note',
            field=models.TextField(verbose_name='Примечание'),
        ),
        migrations.AlterField(
            model_name='task',
            name='deadline',
            field=models.DateField(verbose_name='Срок выполнения'),
        ),
        migrations.AlterField(
            model_name='task',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.department', verbose_name='Отдел'),
        ),
        migrations.AlterField(
            model_name='task',
            name='difficulty',
            field=models.IntegerField(choices=[(1, 'Очень легкая'), (2, 'Легкая'), (3, 'Средняя'), (4, 'Трудная'), (5, 'Очень трудная')], default=1, verbose_name='Сложность'),
        ),
        migrations.AlterField(
            model_name='task',
            name='notifications_sent',
            field=models.IntegerField(default=0, verbose_name='Отправленные уведомления'),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(default='Свободна', max_length=50, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='task',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='taskassignment',
            name='employee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.employee', verbose_name='Сотрудник'),
        ),
        migrations.AlterField(
            model_name='taskassignment',
            name='is_completed',
            field=models.BooleanField(default=False, verbose_name='Завершено'),
        ),
        migrations.AlterField(
            model_name='taskassignment',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.task', verbose_name='Задача'),
        ),
        migrations.AlterField(
            model_name='taskrequest',
            name='employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.employee', verbose_name='Сотрудник'),
        ),
        migrations.AlterField(
            model_name='taskrequest',
            name='task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.task', verbose_name='Задача'),
        ),
    ]
