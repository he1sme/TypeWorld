                                      

from django.conf import settings

from django.db import migrations, models

import django.db.models.deletion

import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [

        ('races', '0002_email_login_code'),

        migrations.swappable_dependency(settings.AUTH_USER_MODEL),

    ]

    operations = [

        migrations.AddField(

            model_name='raceresult',

            name='is_win',

            field=models.BooleanField(default=False),

        ),

        migrations.CreateModel(

            name='UserAchievement',

            fields=[

                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),

                ('code', models.CharField(max_length=64)),

                ('unlocked_at', models.DateTimeField(default=django.utils.timezone.now)),

                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='typeworld_achievements', to=settings.AUTH_USER_MODEL)),

            ],

            options={

                'ordering': ['-unlocked_at'],

                'unique_together': {('user', 'code')},

            },

        ),

    ]
