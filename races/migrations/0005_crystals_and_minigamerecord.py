from django.conf import settings

from django.db import migrations, models

import django.db.models.deletion

import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [

        ('races', '0004_merge_0003_achievements_and_win_0003_userprofile'),

        migrations.swappable_dependency(settings.AUTH_USER_MODEL),

    ]

    operations = [

        migrations.AddField(

            model_name='userprofile',

            name='crystals',

            field=models.PositiveIntegerField(default=0),

        ),

        migrations.CreateModel(

            name='MiniGameRecord',

            fields=[

                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),

                ('game', models.CharField(choices=[('sprint', 'Спринт'), ('falling', 'Падающие слова'), ('reaction', 'Реакция клавиш')], max_length=20)),

                ('score', models.PositiveIntegerField(default=0)),

                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),

                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='typeworld_minigame_records', to=settings.AUTH_USER_MODEL)),

            ],

            options={

                'ordering': ['-created_at'],

            },

        ),

    ]
