import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('races', '0011_alter_minigamerecord_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='minigamerecord',
            name='game_code',
            field=models.CharField(default='sprint', max_length=32),
        ),
        migrations.AddField(
            model_name='minigamerecord',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='minigamerecord',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='minigame_records',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='typeworld_profile',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterModelOptions(
            name='minigamerecord',
            options={'ordering': ['game_code']},
        ),
        migrations.RemoveField(
            model_name='minigamerecord',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='minigamerecord',
            name='game',
        ),
    ]