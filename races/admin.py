from django.contrib import admin

from .models import EmailLoginCode, RaceResult, RaceRoom, TypingText, UserProfile

@admin.register(TypingText)

class TypingTextAdmin(admin.ModelAdmin):

    list_display = ('title', 'author', 'language', 'source', 'created_at')

    search_fields = ('title', 'author', 'content')

@admin.register(RaceRoom)

class RaceRoomAdmin(admin.ModelAdmin):

    list_display = ('code', 'status', 'winner_name', 'created_at', 'started_at')

    search_fields = ('code', 'winner_name')

@admin.register(RaceResult)

class RaceResultAdmin(admin.ModelAdmin):

    list_display = ('player_name', 'room', 'wpm', 'accuracy', 'errors', 'finished_at')

    search_fields = ('player_name',)

@admin.register(EmailLoginCode)

class EmailLoginCodeAdmin(admin.ModelAdmin):

    list_display = ('email', 'code', 'is_used', 'attempts', 'created_at', 'expires_at')

    search_fields = ('email',)

admin.site.register(UserProfile)
