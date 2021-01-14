# Generated by Django 2.2.6 on 2021-01-07 14:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20201214_0429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, help_text='Выберите одну из существующих групп.<p>Не обязательно для заполнения.</p>', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='posts.Group', verbose_name='Группа'),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(help_text='Введите текс поста.<p>* Oбязательно для заполнения.</p>', verbose_name='Текст'),
        ),
    ]