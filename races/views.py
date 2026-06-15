import json

import random

import string

from datetime import timedelta

from django.contrib.auth import login, logout

from django.contrib.auth.models import User

from django.contrib import messages

from django.core.mail import send_mail

from django.db import connection

from django.db.models import Avg, Count, Max

from django.utils import timezone

from django.http import JsonResponse

from django.shortcuts import get_object_or_404, redirect, render

from django.views.decorators.csrf import csrf_exempt

from django.views.decorators.http import require_POST

from .book_api import get_random_gutenberg_fragment

from .achievements import ACHIEVEMENTS, ALL_SKINS, SKIN_REQUIREMENTS, SKIN_PRICES, build_achievement_cards, evaluate_achievements, get_unlocked_skins

from .models import EmailLoginCode, MiniGameRecord, OwnedCar, RaceResult, RaceRoom, TypingText, UserProfile

def ensure_text() -> TypingText:

    if not TypingText.objects.exists():

        title, author, source, content = get_random_gutenberg_fragment('ru')

        return TypingText.objects.create(title=title, author=author, source=source, content=content, language='ru')

    return TypingText.objects.order_by('?').first()

def cleanup_email_codes(email=None):

    qs = EmailLoginCode.objects.filter(expires_at__lt=timezone.now())

    if email:

        qs = qs | EmailLoginCode.objects.filter(email=email, is_used=True)

    qs.delete()

def make_email_code() -> str:

    return ''.join(random.choices(string.digits, k=6))

def username_from_email(email: str) -> str:

    base = ''.join(ch for ch in email.split('@')[0] if ch.isalnum() or ch in '_-')[:24] or 'user'

    username = base

    index = 1

    while User.objects.filter(username=username).exists():

        index += 1

        username = f'{base}{index}'[:30]

    return username

def get_profile(user):

    profile, _ = UserProfile.objects.get_or_create(user=user)

    return profile

def ensure_shop_schema():

    existing = set(connection.introspection.table_names())

    with connection.cursor() as cursor:

        if 'races_userprofile' in existing:

            cursor.execute('PRAGMA table_info(races_userprofile)')

            cols = {row[1] for row in cursor.fetchall()}

            if 'crystals' not in cols:

                cursor.execute('ALTER TABLE races_userprofile ADD COLUMN crystals integer unsigned NOT NULL DEFAULT 0')

        existing = set(connection.introspection.table_names())

        if 'races_minigamerecord' not in existing:

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

            cursor.execute('PRAGMA table_info(races_minigamerecord)')

            cols = {row[1] for row in cursor.fetchall()}

            if 'game_code' not in cols:

                cursor.execute("ALTER TABLE races_minigamerecord ADD COLUMN game_code varchar(32) NOT NULL DEFAULT 'sprint'")

            if 'score' not in cols:

                cursor.execute('ALTER TABLE races_minigamerecord ADD COLUMN score integer unsigned NOT NULL DEFAULT 0')

            if 'updated_at' not in cols:

                cursor.execute("ALTER TABLE races_minigamerecord ADD COLUMN updated_at datetime NOT NULL DEFAULT '2026-01-01 00:00:00'")

        cursor.execute('CREATE INDEX IF NOT EXISTS races_minigamerecord_user_id_idx ON races_minigamerecord(user_id)')

        cursor.execute("""
            DELETE FROM races_minigamerecord
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM races_minigamerecord
                GROUP BY user_id, game_code
            )
        """)

        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS races_minigamerecord_user_game_uniq ON races_minigamerecord(user_id, game_code)')

        existing = set(connection.introspection.table_names())

        if 'races_ownedcar' not in existing:

            cursor.execute("""
                CREATE TABLE races_ownedcar (
                    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    car_code varchar(20) NOT NULL,
                    bought_at datetime NOT NULL,
                    user_id integer NOT NULL REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED
                )
            """)

        cursor.execute('CREATE INDEX IF NOT EXISTS races_ownedcar_user_id_idx ON races_ownedcar(user_id)')

        cursor.execute("""
            DELETE FROM races_ownedcar
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM races_ownedcar
                GROUP BY user_id, car_code
            )
        """)

        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS races_ownedcar_user_car_uniq ON races_ownedcar(user_id, car_code)')

def add_crystals(user, amount=10):

    if not getattr(user, 'is_authenticated', False):

        return 0

    profile = get_profile(user)

    profile.crystals += amount

    profile.save(update_fields=['crystals', 'updated_at'])

    return profile.crystals

def home(request):

    ensure_text()

    results = RaceResult.objects.select_related('room')[:10]

    rooms = RaceRoom.objects.order_by('-created_at')[:8]

    return render(request, 'races/home.html', {'results': results, 'rooms': rooms})

def leaderboard(request):

    results = RaceResult.objects.select_related('room', 'user', 'user__typeworld_profile')[:50]

    return render(request, 'races/leaderboard.html', {'results': results})

def race_solo(request):

    text = ensure_text()

    return render(request, 'races/race_solo.html', {'text': text})

def buy_crystals_page(request):

    ensure_shop_schema()

    if not request.user.is_authenticated:

        return redirect('login')

    packs = [

        {'amount': 25, 'price': 25},

        {'amount': 50, 'price': 45},

        {'amount': 100, 'price': 85},

        {'amount': 250, 'price': 199},

        {'amount': 500, 'price': 349},

    ]

    profile = get_profile(request.user)

    if request.method == 'POST':

        try:

            amount = int(request.POST.get('amount', '0'))

        except (TypeError, ValueError):

            amount = 0

        amount = max(1, min(amount, 10000))

        price = calculate_crystal_price(amount)

        profile.crystals += amount

        profile.save(update_fields=['crystals', 'updated_at'])

        messages.success(request, f'Покупка успешно оформлена: +{amount} 💎 за {price} ₽.')

        return redirect('buy_crystals')

    return render(request, 'races/buy_crystals.html', {

        'packs': packs,

        'crystals': profile.crystals,

    })

def calculate_crystal_price(amount):

    if amount >= 500:

        return round(amount * 0.70)

    if amount >= 250:

        return round(amount * 0.80)

    if amount >= 100:

        return round(amount * 0.85)

    if amount >= 50:

        return round(amount * 0.90)

    return amount

def shop(request):

    base_names = {

        'car_01': 'Классика',

        'car_02': 'Хэтчбек',

        'car_03': 'Жёлтый спорт',

        'car_04': 'Кроссовер',

        'car_05': 'Оранжевый суперкар',

        'car_06': 'Ралли',

        'car_07': 'Фиолетовый тюнинг',

        'car_08': 'Кибер-пикап',

        'car_09': 'Зелёный гиперкар',

        'car_10': 'Футуристичный болид',

        'car_11': 'Красный болид',

        'cyber_01': 'Неоновый гиперкар',

        'cyber_02': 'Тайм-раннер',

        'cyber_03': 'Кибер-мотоцикл',

        'cyber_04': 'Кибер-пикап X',

        'cyber_05': 'Ховербайк',

        'cyber_06': 'Фиолетовый фантом',

        'cyber_07': 'Полиция будущего',

        'cyber_08': 'Ночной страж',

        'cyber_09': 'Грузовик будущего',

        'cyber_10': 'Формула Neon X',

    }

    achievement_by_code = {item['code']: item for item in ACHIEVEMENTS}

    unlocked = set(get_unlocked_skins(request.user))

    crystals = 0

    current_skin = 'car_01'

    if request.user.is_authenticated:

        profile = get_profile(request.user)

        crystals = profile.crystals

        current_skin = profile.car_skin

    skins = []

    for skin_id in ALL_SKINS:

        required_code = SKIN_REQUIREMENTS.get(skin_id)

        achievement = achievement_by_code.get(required_code) if required_code else None

        price = SKIN_PRICES.get(skin_id, 0)

        skins.append({

            'id': skin_id,

            'name': base_names.get(skin_id, skin_id),

            'unlocked': skin_id in unlocked,

            'achievement': achievement,

            'price': price,

            'buyable': price > 0 and skin_id not in unlocked,

        })

    return render(request, 'races/shop.html', {'skins': skins, 'unlocked_skins': list(unlocked), 'crystals': crystals, 'current_skin': current_skin})

@require_POST

def buy_car(request, skin_id):

    ensure_shop_schema()

    if not request.user.is_authenticated:

        return redirect('login')

    if skin_id not in SKIN_PRICES:

        messages.error(request, 'Эту машинку нельзя купить.')

        return redirect('shop')

    if OwnedCar.objects.filter(user=request.user, car_code=skin_id).exists():

        messages.info(request, 'Эта машинка уже куплена.')

        return redirect('shop')

    profile = get_profile(request.user)

    price = SKIN_PRICES[skin_id]

    if profile.crystals < price:

        messages.error(request, 'Недостаточно кристалликов.')

        return redirect('shop')

    profile.crystals -= price

    profile.car_skin = skin_id

    profile.save(update_fields=['crystals', 'car_skin', 'updated_at'])

    OwnedCar.objects.create(user=request.user, car_code=skin_id)

    messages.success(request, 'Машинка куплена и выбрана.')

    return redirect('shop')

@require_POST

def select_car(request, skin_id):

    ensure_shop_schema()

    if not request.user.is_authenticated:

        return redirect('login')

    unlocked = set(get_unlocked_skins(request.user))

    if skin_id not in unlocked:

        messages.error(request, 'Эта машинка ещё не открыта или не куплена.')

        return redirect('shop')

    profile = get_profile(request.user)

    profile.car_skin = skin_id

    profile.save(update_fields=['car_skin', 'updated_at'])

    messages.success(request, 'Машинка выбрана.')

    return redirect('shop')

def achievements(request):

    if not request.user.is_authenticated:

        return redirect('login')

    cards = build_achievement_cards(request.user)

    unlocked_skins = get_unlocked_skins(request.user)

    return render(request, 'races/achievements.html', {'achievements': cards, 'unlocked_skins': unlocked_skins})

def make_code() -> str:

    while True:

        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        if not RaceRoom.objects.filter(code=code).exists():

            return code

def create_room(request):

    title, author, source, content = get_random_gutenberg_fragment('ru')

    text = TypingText.objects.create(title=title, author=author, source=source, content=content, language='ru')

    room = RaceRoom.objects.create(code=make_code(), text=text)

    return redirect('room', code=room.code)

def join_room(request):

    code = request.POST.get('code', '').strip().upper()

    if not code:

        return redirect('home')

    return redirect('room', code=code)

def room(request, code):

    room_obj = get_object_or_404(RaceRoom, code=code.upper())

    player_name = request.user.username if request.user.is_authenticated else f'Player{random.randint(100, 999)}'

    current_skin = 'car_01'

    if request.user.is_authenticated:

        current_skin = get_profile(request.user).car_skin

    return render(request, 'races/room.html', {

        'room': room_obj,

        'player_name': player_name,

        'unlocked_skins': get_unlocked_skins(request.user),

        'current_skin': current_skin,

    })

@csrf_exempt

@require_POST

def save_result(request):

    data = json.loads(request.body.decode('utf-8'))

    room = None

    if data.get('room_code'):

        room = RaceRoom.objects.filter(code=data.get('room_code')).first()

    result = RaceResult.objects.create(

        user=request.user if request.user.is_authenticated else None,

        room=room,

        player_name=data.get('player_name') or (request.user.username if request.user.is_authenticated else 'Игрок'),

        wpm=int(data.get('wpm', 0)),

        accuracy=float(data.get('accuracy', 0)),

        errors=int(data.get('errors', 0)),

        is_win=bool(data.get('is_win', False)),

    )

    unlocked = evaluate_achievements(result.user, result) if result.user else []

    crystals = None

    if result.user:

        crystals = add_crystals(result.user, 10)

    return JsonResponse({'ok': True, 'unlocked': unlocked, 'crystals': crystals})

def login_view(request):

    if request.user.is_authenticated:

        return redirect('profile')

    return render(request, 'races/login.html')

def email_login_start(request):

    if request.user.is_authenticated:

        return redirect('profile')

    if request.method == 'POST':

        email = (request.POST.get('email') or '').strip().lower()

        if not email or '@' not in email:

            messages.error(request, 'Введите корректную почту.')

            return render(request, 'races/email_login_start.html')

        cleanup_email_codes(email)

        code = make_email_code()

        EmailLoginCode.objects.create(

            email=email,

            code=code,

            expires_at=timezone.now() + timedelta(minutes=10),

        )

        request.session['pending_login_email'] = email

        send_mail(

            subject='Код входа TypeWorld',

            message=f'Ваш код входа в TypeWorld: {code}\n\nКод действует 10 минут.',

            from_email=None,

            recipient_list=[email],

            fail_silently=False,

        )

        messages.success(request, 'Код отправлен на указанную почту.')

        return redirect('email_login_verify')

    return render(request, 'races/email_login_start.html')

def email_login_verify(request):

    if request.user.is_authenticated:

        return redirect('profile')

    email = request.session.get('pending_login_email')

    if not email:

        return redirect('email_login_start')

    if request.method == 'POST':

        code = ''.join(ch for ch in (request.POST.get('code') or '') if ch.isdigit())[:6]

        obj = EmailLoginCode.objects.filter(email=email, is_used=False).order_by('-created_at').first()

        if not obj or obj.is_expired:

            messages.error(request, 'Код устарел. Запросите новый код.')

            return redirect('email_login_start')

        if obj.attempts >= 5:

            messages.error(request, 'Слишком много попыток. Запросите новый код.')

            return redirect('email_login_start')

        if obj.code != code:

            obj.attempts += 1

            obj.save(update_fields=['attempts'])

            messages.error(request, 'Неверный код.')

            return render(request, 'races/email_login_verify.html', {'email': email})

        obj.is_used = True

        obj.save(update_fields=['is_used'])

        user = User.objects.filter(email__iexact=email).first()

        if not user:

            user = User.objects.create_user(username=username_from_email(email), email=email)

            user.set_unusable_password()

            user.save(update_fields=['password'])

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        request.session.pop('pending_login_email', None)

        return redirect('profile')

    return render(request, 'races/email_login_verify.html', {'email': email})

def profile(request):

    ensure_shop_schema()

    if not request.user.is_authenticated:

        return redirect('login')

    user_results = RaceResult.objects.filter(user=request.user)

    profile_obj = get_profile(request.user)

    context = {

        'profile_obj': profile_obj,

        'crystals': profile_obj.crystals,

        'records': MiniGameRecord.objects.filter(user=request.user),

        'results_count': user_results.count(),

        'best_wpm': user_results.aggregate(Max('wpm')).get('wpm__max') or 0,

        'avg_accuracy': user_results.aggregate(Avg('accuracy')).get('accuracy__avg') or 0,

        'recent_results': user_results.order_by('-finished_at')[:10],

        'social_count': request.user.socialaccount_set.count() if hasattr(request.user, 'socialaccount_set') else 0,

        'achievements': build_achievement_cards(request.user),

        'unlocked_skins': get_unlocked_skins(request.user),

    }

    return render(request, 'races/profile.html', context)

def public_profile(request, user_id):

    ensure_shop_schema()

    viewed_user = get_object_or_404(User, pk=user_id)

    profile_obj = get_profile(viewed_user)

    user_results = RaceResult.objects.filter(user=viewed_user)

    context = {

        'viewed_user': viewed_user,

        'profile_obj': profile_obj,

        'records': MiniGameRecord.objects.filter(user=viewed_user),

        'results_count': user_results.count(),

        'best_wpm': user_results.aggregate(Max('wpm')).get('wpm__max') or 0,

        'avg_accuracy': user_results.aggregate(Avg('accuracy')).get('accuracy__avg') or 0,

        'recent_results': user_results.order_by('-finished_at')[:10],

        'achievements': build_achievement_cards(viewed_user),

        'unlocked_skins': get_unlocked_skins(viewed_user),

    }

    return render(request, 'races/public_profile.html', context)

def edit_profile(request):

    if not request.user.is_authenticated:

        return redirect('login')

    profile_obj = get_profile(request.user)

    if request.method == 'POST':

        username = (request.POST.get('username') or '').strip()[:30]

        if not username:

            messages.error(request, 'Логин не может быть пустым.')

            return redirect('edit_profile')

        if User.objects.exclude(pk=request.user.pk).filter(username__iexact=username).exists():

            messages.error(request, 'Такой логин уже занят.')

            return redirect('edit_profile')

        request.user.username = username

        request.user.first_name = (request.POST.get('first_name') or '').strip()[:150]

        request.user.last_name = (request.POST.get('last_name') or '').strip()[:150]

        request.user.save(update_fields=['username', 'first_name', 'last_name'])

        profile_obj.display_name = (request.POST.get('display_name') or '').strip()[:40]

        profile_obj.bio = (request.POST.get('bio') or '').strip()[:160]

        profile_obj.avatar_url = ''

        profile_obj.save()

        messages.success(request, 'Профиль сохранён.')

        return redirect('profile')

    return render(request, 'races/edit_profile.html', {'profile_obj': profile_obj})

@csrf_exempt

@require_POST

def save_minigame_record(request):

    ensure_shop_schema()

    if not request.user.is_authenticated:

        return JsonResponse({'ok': False, 'message': 'Войдите в аккаунт, чтобы получать кристаллики.'})

    data = json.loads(request.body.decode('utf-8'))

    game_code = (data.get('game') or '').strip()[:32]

    score = max(0, int(data.get('score', 0)))

    if game_code not in {'sprint', 'falling', 'reaction'} or score <= 0:

        return JsonResponse({'ok': False, 'message': 'Некорректный результат.'})

    lower_is_better = game_code == 'reaction'

    record, created = MiniGameRecord.objects.get_or_create(user=request.user, game_code=game_code, defaults={'score': score})

    is_record = created or (score < record.score if lower_is_better else score > record.score)

    if is_record:

        record.score = score

        record.save(update_fields=['score', 'updated_at'])

    crystals = add_crystals(request.user, 10)

    return JsonResponse({'ok': True, 'new_record': is_record, 'crystals': crystals, 'best': record.score})

def logout_view(request):

    logout(request)

    return redirect('home')

def games(request):

    return render(request, "races/games.html")

def game_sprint(request):

    return render(request, "races/game_sprint.html")

def game_falling(request):

    return render(request, "races/game_falling.html")

def game_falling_words(request):

    return render(request, "races/game_falling.html")

def game_reaction(request):

    return render(request, "races/game_reaction.html")
