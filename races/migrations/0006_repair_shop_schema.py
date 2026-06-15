from django.db import migrations

def repair_schema(apps, schema_editor):

    connection = schema_editor.connection

    def table_names():

        return set(connection.introspection.table_names())

    def columns(table):

        with connection.cursor() as cursor:

            cursor.execute(f'PRAGMA table_info({table})')

            return {row[1] for row in cursor.fetchall()}

    with connection.cursor() as cursor:

        existing = table_names()

        if 'races_userprofile' in existing:

            cols = columns('races_userprofile')

            if 'crystals' not in cols:

                cursor.execute('ALTER TABLE races_userprofile ADD COLUMN crystals integer unsigned NOT NULL DEFAULT 0')

        if 'races_minigamerecord' not in existing:

            cursor.execute('''
                CREATE TABLE races_minigamerecord (
                    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    game_code varchar(32) NOT NULL DEFAULT 'sprint',
                    score integer unsigned NOT NULL DEFAULT 0,
                    updated_at datetime NOT NULL,
                    user_id integer NOT NULL REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED
                )
            ''')

        else:

            cols = columns('races_minigamerecord')

            if 'game_code' not in cols:

                cursor.execute("ALTER TABLE races_minigamerecord ADD COLUMN game_code varchar(32) NOT NULL DEFAULT 'sprint'")

            if 'score' not in cols:

                cursor.execute('ALTER TABLE races_minigamerecord ADD COLUMN score integer unsigned NOT NULL DEFAULT 0')

            if 'updated_at' not in cols:

                cursor.execute("ALTER TABLE races_minigamerecord ADD COLUMN updated_at datetime NOT NULL DEFAULT '2026-01-01 00:00:00'")

        cursor.execute('CREATE INDEX IF NOT EXISTS races_minigamerecord_user_id_idx ON races_minigamerecord(user_id)')

        cursor.execute('''
            DELETE FROM races_minigamerecord
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM races_minigamerecord
                GROUP BY user_id, game_code
            )
        ''')

        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS races_minigamerecord_user_game_uniq ON races_minigamerecord(user_id, game_code)')

        if 'races_ownedcar' not in table_names():

            cursor.execute('''
                CREATE TABLE races_ownedcar (
                    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    car_code varchar(20) NOT NULL,
                    bought_at datetime NOT NULL,
                    user_id integer NOT NULL REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED
                )
            ''')

        cursor.execute('CREATE INDEX IF NOT EXISTS races_ownedcar_user_id_idx ON races_ownedcar(user_id)')

        cursor.execute('''
            DELETE FROM races_ownedcar
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM races_ownedcar
                GROUP BY user_id, car_code
            )
        ''')

        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS races_ownedcar_user_car_uniq ON races_ownedcar(user_id, car_code)')

class Migration(migrations.Migration):

    dependencies = [

        ('races', '0006_merge_20260604_1747'),

    ]

    operations = [

        migrations.RunPython(repair_schema, migrations.RunPython.noop),

    ]
