                                         

from django.db import migrations, models

import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [

        ('races', '0001_initial'),

    ]

    operations = [

        migrations.CreateModel(

            name='EmailLoginCode',

            fields=[

                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),

                ('email', models.EmailField(db_index=True, max_length=254)),

                ('code', models.CharField(max_length=6)),

                ('attempts', models.PositiveIntegerField(default=0)),

                ('is_used', models.BooleanField(default=False)),

                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),

                ('expires_at', models.DateTimeField()),

            ],

            options={'ordering': ['-created_at']},

        ),

    ]
