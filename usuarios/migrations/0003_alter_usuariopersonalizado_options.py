# Generated by Django 5.1.6 on 2025-02-23 16:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_rol_usuariopersonalizado_rol'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usuariopersonalizado',
            options={'verbose_name': 'Usuario', 'verbose_name_plural': 'Usuarios'},
        ),
    ]
