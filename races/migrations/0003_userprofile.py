                                         

from django.conf import settings

from django.db import migrations, models

import django.db.models.deletion

def create_profiles(apps, schema_editor):

    User = apps.get_model('auth', 'User')

    UserProfile = apps.get_model('races', 'UserProfile')

    for user in User.objects.all():

        UserProfile.objects.get_or_create(user=user, defaults={'display_name': user.username})

class Migration(migrations.Migration):

    dependencies = [

        migrations.swappable_dependency(settings.AUTH_USER_MODEL),

        ('races', '0002_email_login_code'),

    ]

    operations = [

        migrations.CreateModel(

            name='UserProfile',

            fields=[

                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),

                ('display_name', models.CharField(blank=True, default='', max_length=40)),

                ('bio', models.CharField(blank=True, default='', max_length=160)),

                ('avatar_url', models.URLField(blank=True, default='')),

                ('car_skin', models.CharField(default='car_01', max_length=20)),

                ('updated_at', models.DateTimeField(auto_now=True)),

                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),

            ],

        ),

        migrations.RunPython(create_profiles, migrations.RunPython.noop),

    ]
