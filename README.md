# TypeWorld

Django-проект онлайн-гонок по набору текста.

## Запуск

```bash
python -m venv venv
source venv/bin/activate(для Windows venv\Scripts\Activate.ps1)
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Для Windows используйте `venv\Scripts\activate`. Настройки берутся из `.env`; пример лежит в `.env.example`.
