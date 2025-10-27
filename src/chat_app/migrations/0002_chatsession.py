# Generated migration for ChatSession model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat_app', '0001_initial'),  # Asume que existe una migración inicial
    ]

    operations = [
        migrations.CreateModel(
            name='ChatSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(default='Nueva conversación', max_length=200)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-actualizado_en'],
            },
        ),
        migrations.AddField(
            model_name='chat',
            name='session',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mensajes', to='chat_app.chatsession'),
        ),
        migrations.AlterModelOptions(
            name='chat',
            options={'ordering': ['fecha']},
        ),
    ]
