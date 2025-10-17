from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region', models.CharField(blank=True, default='', max_length=100)),
                ('comuna', models.CharField(blank=True, default='', max_length=100)),
                ('telefono', models.CharField(blank=True, default='', max_length=50)),
                ('rut', models.CharField(blank=True, default='', max_length=20)),
                ('direccion', models.CharField(blank=True, default='', max_length=255)),
                ('sede', models.CharField(blank=True, default='', max_length=100)),
                ('facultades', models.JSONField(blank=True, default=list)),
                ('carreras', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
