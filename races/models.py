from django.contrib.auth.models import User

from django.db import models

from django.utils import timezone

CAR_CHOICES = [

    ('car_01', 'Классика'), ('car_02', 'Хэтчбек'), ('car_03', 'Жёлтый спорт'),

    ('car_04', 'Кроссовер'), ('car_05', 'Оранжевый суперкар'), ('car_06', 'Ралли'),

    ('car_07', 'Фиолетовый тюнинг'), ('car_08', 'Кибер-пикап'), ('car_09', 'Зелёный гиперкар'),

    ('car_10', 'Футуристичный болид'), ('car_11', 'Красный болид'),

    ('cyber_01', 'Неоновый гиперкар'), ('cyber_02', 'Тайм-раннер'),

    ('cyber_03', 'Кибер-мотоцикл'), ('cyber_04', 'Кибер-пикап X'),

    ('cyber_05', 'Ховербайк'), ('cyber_06', 'Фиолетовый фантом'),

    ('cyber_07', 'Полиция будущего'), ('cyber_08', 'Ночной страж'),

    ('cyber_09', 'Грузовик будущего'), ('cyber_10', 'Формула Neon X'),

]

class TypingText(models.Model):

    title = models.CharField(max_length=255, default='Текст')

    author = models.CharField(max_length=255, blank=True, default='')

    source = models.CharField(max_length=255, blank=True, default='')

    language = models.CharField(max_length=10, default='en')

    content = models.TextField()

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):

        return self.title

class RaceRoom(models.Model):

    code = models.SlugField(max_length=32, unique=True)

    text = models.ForeignKey(TypingText, on_delete=models.SET_NULL, null=True, blank=True)

    status = models.CharField(max_length=20, default='waiting')

    winner_name = models.CharField(max_length=80, blank=True, default='')

    created_at = models.DateTimeField(default=timezone.now)

    started_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):

        return self.code

class RaceResult(models.Model):

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    room = models.ForeignKey(RaceRoom, on_delete=models.SET_NULL, null=True, blank=True)

    player_name = models.CharField(max_length=80, default='Игрок')

    wpm = models.PositiveIntegerField(default=0)

    accuracy = models.FloatField(default=0)

    errors = models.PositiveIntegerField(default=0)

    is_win = models.BooleanField(default=False)

    finished_at = models.DateTimeField(default=timezone.now)

    class Meta:

        ordering = ['-wpm', '-accuracy', 'errors']

    def __str__(self):

        return f'{self.player_name}: {self.wpm} WPM'

class EmailLoginCode(models.Model):

    email = models.EmailField(db_index=True)

    code = models.CharField(max_length=6)

    attempts = models.PositiveIntegerField(default=0)

    is_used = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)

    expires_at = models.DateTimeField()

    class Meta:

        ordering = ['-created_at']

    def __str__(self):

        return f'{self.email}: {self.code}'

    @property

    def is_expired(self):

        return timezone.now() > self.expires_at

class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='typeworld_profile')

    display_name = models.CharField(max_length=40, blank=True, default='')

    bio = models.CharField(max_length=160, blank=True, default='')

    avatar_url = models.URLField(blank=True, default='')

    car_skin = models.CharField(max_length=20, choices=CAR_CHOICES, default='car_01')

    crystals = models.PositiveIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    @property

    def public_name(self):

        return self.display_name.strip() or self.user.username

    def __str__(self):

        return self.public_name

class OwnedCar(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_cars')

    car_code = models.CharField(max_length=20)

    bought_at = models.DateTimeField(default=timezone.now)

    class Meta:

        unique_together = ('user', 'car_code')

        ordering = ['car_code']

    def __str__(self):

        return f'{self.user.username}: {self.car_code}'

class MiniGameRecord(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='minigame_records')

    game_code = models.CharField(max_length=32, default='sprint')

    score = models.PositiveIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:

        unique_together = ('user', 'game_code')

        ordering = ['game_code']

    def __str__(self):

        return f'{self.user.username}: {self.game_code} = {self.score}'

class UserAchievement(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='typeworld_achievements')

    code = models.CharField(max_length=64)

    unlocked_at = models.DateTimeField(default=timezone.now)

    class Meta:

        unique_together = ('user', 'code')

        ordering = ['-unlocked_at']

    def __str__(self):

        return f'{self.user.username}: {self.code}'
