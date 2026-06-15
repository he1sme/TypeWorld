from django.conf import settings

from django.db import migrations, models

import django.db.models.deletion

import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [

        migrations.swappable_dependency(settings.AUTH_USER_MODEL),

        ('races', '0004_merge_0003_achievements_and_win_0003_userprofile'),

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

                ('game_code', models.CharField(max_length=32)),

                ('score', models.PositiveIntegerField(default=0)),

                ('updated_at', models.DateTimeField(auto_now=True)),

                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='minigame_records', to=settings.AUTH_USER_MODEL)),

            ],

            options={

                'ordering': ['game_code'],

                'unique_together': {('user', 'game_code')},

            },

        ),

        migrations.CreateModel(

            name='OwnedCar',

            fields=[

                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),

                ('car_code', models.CharField(max_length=20)),

                ('bought_at', models.DateTimeField(default=django.utils.timezone.now)),

                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_cars', to=settings.AUTH_USER_MODEL)),

            ],

            options={

                'ordering': ['car_code'],

                'unique_together': {('user', 'car_code')},

            },

        ),

        migrations.AlterField(

            model_name='userprofile',

            name='car_skin',

            field=models.CharField(choices=[('car_01', 'Классика'), ('car_02', 'Хэтчбек'), ('car_03', 'Жёлтый спорт'), ('car_04', 'Кроссовер'), ('car_05', 'Оранжевый суперкар'), ('car_06', 'Ралли'), ('car_07', 'Фиолетовый тюнинг'), ('car_08', 'Кибер-пикап'), ('car_09', 'Зелёный гиперкар'), ('car_10', 'Футуристичный болид'), ('car_11', 'Красный болид'), ('cyber_01', 'Неоновый гиперкар'), ('cyber_02', 'Тайм-раннер'), ('cyber_03', 'Кибер-мотоцикл'), ('cyber_04', 'Кибер-пикап X'), ('cyber_05', 'Ховербайк'), ('cyber_06', 'Фиолетовый фантом'), ('cyber_07', 'Полиция будущего'), ('cyber_08', 'Ночной страж'), ('cyber_09', 'Грузовик будущего'), ('cyber_10', 'Формула Neon X')], default='car_01', max_length=20),

        ),

    ]
