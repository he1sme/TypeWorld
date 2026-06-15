                                                       

from django.conf import settings

from django.db import migrations, models, connection

import django.db.models.deletion

def table_exists(cursor, table_name):

    return table_name in [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]

def column_exists(cursor, table_name, column_name):

    if not table_exists(cursor, table_name):

        return False

    return column_name in [row[1] for row in cursor.execute(f"PRAGMA table_info({table_name})").fetchall()]

def repair_schema(apps, schema_editor):

    with connection.cursor() as cursor:

        if table_exists(cursor, "races_userprofile") and not column_exists(cursor, "races_userprofile", "crystals"):

            cursor.execute("ALTER TABLE races_userprofile ADD COLUMN crystals integer unsigned NOT NULL DEFAULT 0")

        if not table_exists(cursor, "races_minigamerecord"):

            cursor.execute("""
                CREATE TABLE races_minigamerecord (
                    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    game_code varchar(32) NOT NULL DEFAULT 'sprint',
                    score integer unsigned NOT NULL DEFAULT 0,
                    updated_at datetime NOT NULL,
                    user_id integer NOT NULL REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED
                )
            """)

        else:

            if not column_exists(cursor, "races_minigamerecord", "game_code"):

                cursor.execute("ALTER TABLE races_minigamerecord ADD COLUMN game_code varchar(32) NOT NULL DEFAULT 'sprint'")

            if not column_exists(cursor, "races_minigamerecord", "score"):

                cursor.execute("ALTER TABLE races_minigamerecord ADD COLUMN score integer unsigned NOT NULL DEFAULT 0")

            if not column_exists(cursor, "races_minigamerecord", "updated_at"):

                cursor.execute("ALTER TABLE races_minigamerecord ADD COLUMN updated_at datetime NOT NULL DEFAULT '2026-01-01 00:00:00'")

            if not column_exists(cursor, "races_minigamerecord", "user_id"):

                cursor.execute("ALTER TABLE races_minigamerecord ADD COLUMN user_id integer NULL REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED")

        if table_exists(cursor, "races_minigamerecord"):

            cursor.execute("""
                DELETE FROM races_minigamerecord
                WHERE id NOT IN (
                    SELECT MIN(id)
                    FROM races_minigamerecord
                    GROUP BY user_id, game_code
                )
            """)

            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS races_minigamerecord_user_game_uniq ON races_minigamerecord(user_id, game_code)")

class Migration(migrations.Migration):

    dependencies = [

        ('races', '0004_merge_0003_achievements_and_win_0003_userprofile'),

        migrations.swappable_dependency(settings.AUTH_USER_MODEL),

    ]

    operations = [

        migrations.SeparateDatabaseAndState(

            database_operations=[

                migrations.RunPython(repair_schema, migrations.RunPython.noop),

            ],

            state_operations=[

                migrations.AddField(

                    model_name='userprofile',

                    name='crystals',

                    field=models.PositiveIntegerField(default=0),

                ),

                migrations.CreateModel(

                    name='MiniGameRecord',

                    fields=[

                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),

                        ('game_code', models.CharField(default='sprint', max_length=32)),

                        ('score', models.PositiveIntegerField(default=0)),

                        ('updated_at', models.DateTimeField(auto_now=True)),

                        ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='minigame_records', to=settings.AUTH_USER_MODEL)),

                    ],

                    options={

                        'ordering': ['game_code'],

                        'unique_together': {('user', 'game_code')},

                    },

                ),

            ],

        ),

    ]
