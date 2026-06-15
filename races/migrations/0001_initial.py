                                               

import django.db.models.deletion

import django.utils.timezone

from django.conf import settings

from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = [

        migrations.swappable_dependency(settings.AUTH_USER_MODEL),

    ]

    operations = [

        migrations.CreateModel(

            name='RaceRoom',

            fields=[

                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),

                ('code', models.SlugField(max_length=32, unique=True)),

                ('status', models.CharField(default='waiting', max_length=20)),

                ('winner_name', models.CharField(blank=True, default='', max_length=80)),

                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),

                ('started_at', models.DateTimeField(blank=True, null=True)),

            ],

        ),

        migrations.CreateModel(

            name='TypingText',

            fields=[

                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),

                ('title', models.CharField(default='Текст', max_length=255)),

                ('author', models.CharField(blank=True, default='', max_length=255)),

                ('source', models.CharField(blank=True, default='', max_length=255)),

                ('language', models.CharField(default='en', max_length=10)),

                ('content', models.TextField()),

                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),

            ],

        ),

        migrations.CreateModel(

            name='RaceResult',

            fields=[

                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),

                ('player_name', models.CharField(default='Игрок', max_length=80)),

                ('wpm', models.PositiveIntegerField(default=0)),

                ('accuracy', models.FloatField(default=0)),

                ('errors', models.PositiveIntegerField(default=0)),

                ('finished_at', models.DateTimeField(default=django.utils.timezone.now)),

                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),

                ('room', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='races.raceroom')),

            ],

            options={

                'ordering': ['-wpm', '-accuracy', 'errors'],

            },

        ),

        migrations.AddField(

            model_name='raceroom',

            name='text',

            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='races.typingtext'),

        ),

    ]
