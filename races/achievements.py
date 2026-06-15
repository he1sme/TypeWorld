from django.db.models import Max

ACHIEVEMENTS = [

    {

        'code': 'first_race',

        'title': 'Первый заезд',

        'description': 'Завершить первую гонку.',

        'skin': 'car_02',

        'skin_name': 'Хэтчбек',

    },

    {

        'code': 'three_races',

        'title': 'На старте уверенно',

        'description': 'Завершить 3 гонки.',

        'skin': 'car_03',

        'skin_name': 'Жёлтый спорт',

    },

    {

        'code': 'ten_races',

        'title': 'Постоянный гонщик',

        'description': 'Завершить 10 гонок.',

        'skin': 'car_04',

        'skin_name': 'Кроссовер',

    },

    {

        'code': 'speed_60',

        'title': '60 WPM',

        'description': 'Показать скорость 60 WPM или выше.',

        'skin': 'car_05',

        'skin_name': 'Оранжевый суперкар',

    },

    {

        'code': 'speed_90',

        'title': '90 WPM',

        'description': 'Показать скорость 90 WPM или выше.',

        'skin': 'car_06',

        'skin_name': 'Ралли',

    },

    {

        'code': 'accuracy_95',

        'title': 'Точная печать',

        'description': 'Завершить гонку с точностью 95% или выше.',

        'skin': 'car_07',

        'skin_name': 'Фиолетовый тюнинг',

    },

    {

        'code': 'accuracy_100',

        'title': 'Безошибочно',

        'description': 'Завершить гонку со 100% точностью.',

        'skin': 'car_08',

        'skin_name': 'Кибер-пикап',

    },

    {

        'code': 'zero_errors',

        'title': 'Чистый финиш',

        'description': 'Завершить гонку без ошибок.',

        'skin': 'car_09',

        'skin_name': 'Зелёный гиперкар',

    },

    {

        'code': 'first_win',

        'title': 'Первая победа',

        'description': 'Победить в онлайн-гонке.',

        'skin': 'car_10',

        'skin_name': 'Футуристичный болид',

    },

    {

        'code': 'twenty_races',

        'title': 'Легенда трассы',

        'description': 'Завершить 20 гонок.',

        'skin': 'car_11',

        'skin_name': 'Красный болид',

    },

]

ACHIEVEMENT_BY_CODE = {item['code']: item for item in ACHIEVEMENTS}

SKIN_REQUIREMENTS = {item['skin']: item['code'] for item in ACHIEVEMENTS if item.get('skin')}

DEFAULT_SKIN = 'car_01'

PURCHASABLE_SKINS = [

    'cyber_01','cyber_02','cyber_03','cyber_04','cyber_05',

    'cyber_06','cyber_07','cyber_08','cyber_09','cyber_10',

]

SKIN_PRICES = {skin: 10 for skin in PURCHASABLE_SKINS}

ALL_SKINS = ['car_01'] + [item['skin'] for item in ACHIEVEMENTS if item.get('skin')] + PURCHASABLE_SKINS

def get_unlocked_codes(user):

    if not getattr(user, 'is_authenticated', False):

        return set()

    from .models import UserAchievement

    return set(UserAchievement.objects.filter(user=user).values_list('code', flat=True))

def get_unlocked_skins(user):

    codes = get_unlocked_codes(user)

    skins = {DEFAULT_SKIN}

    for item in ACHIEVEMENTS:

        if item['code'] in codes and item.get('skin'):

            skins.add(item['skin'])

    if getattr(user, 'is_authenticated', False):

        try:

            from .models import OwnedCar

            skins.update(OwnedCar.objects.filter(user=user).values_list('car_code', flat=True))

        except Exception:

            pass

    return sorted(skins, key=lambda x: ALL_SKINS.index(x) if x in ALL_SKINS else 999)

def build_achievement_cards(user):

    codes = get_unlocked_codes(user)

    return [{**item, 'unlocked': item['code'] in codes} for item in ACHIEVEMENTS]

def unlock_achievement(user, code):

    if not getattr(user, 'is_authenticated', False):

        return False

    from .models import UserAchievement

    _, created = UserAchievement.objects.get_or_create(user=user, code=code)

    return created

def evaluate_achievements(user, result=None):

    if not getattr(user, 'is_authenticated', False):

        return []

    from .models import RaceResult

    qs = RaceResult.objects.filter(user=user)

    count = qs.count()

    best_wpm = qs.aggregate(Max('wpm')).get('wpm__max') or 0

    wins = qs.filter(is_win=True).count()

    unlocked = []

    if count >= 1 and unlock_achievement(user, 'first_race'):

        unlocked.append('first_race')

    if count >= 3 and unlock_achievement(user, 'three_races'):

        unlocked.append('three_races')

    if count >= 10 and unlock_achievement(user, 'ten_races'):

        unlocked.append('ten_races')

    if count >= 20 and unlock_achievement(user, 'twenty_races'):

        unlocked.append('twenty_races')

    if best_wpm >= 60 and unlock_achievement(user, 'speed_60'):

        unlocked.append('speed_60')

    if best_wpm >= 90 and unlock_achievement(user, 'speed_90'):

        unlocked.append('speed_90')

    if wins >= 1 and unlock_achievement(user, 'first_win'):

        unlocked.append('first_win')

    if result is not None:

        if result.accuracy >= 95 and unlock_achievement(user, 'accuracy_95'):

            unlocked.append('accuracy_95')

        if result.accuracy >= 100 and unlock_achievement(user, 'accuracy_100'):

            unlocked.append('accuracy_100')

        if result.errors == 0 and unlock_achievement(user, 'zero_errors'):

            unlocked.append('zero_errors')

    return unlocked
