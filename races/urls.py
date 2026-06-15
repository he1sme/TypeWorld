from django.urls import path

from . import views

urlpatterns = [

    path('', views.home, name='home'),

    path('leaderboard/', views.leaderboard, name='leaderboard'),

    path('solo/', views.race_solo, name='race_solo'),

    path('shop/', views.shop, name='shop'),

    path('crystals/', views.buy_crystals_page, name='buy_crystals'),

    path('shop/buy/<str:skin_id>/', views.buy_car, name='buy_car'),

    path('shop/select/<str:skin_id>/', views.select_car, name='select_car'),

    path('achievements/', views.achievements, name='achievements'),

    path('room/create/', views.create_room, name='create_room'),

    path('room/join/', views.join_room, name='join_room'),

    path('room/<slug:code>/', views.room, name='room'),

    path('api/result/', views.save_result, name='save_result'),

    path('api/minigame-record/', views.save_minigame_record, name='save_minigame_record'),

    path('login/', views.login_view, name='login'),

    path('login/email/', views.email_login_start, name='email_login_start'),

    path('login/email/verify/', views.email_login_verify, name='email_login_verify'),

    path('profile/', views.profile, name='profile'),

    path('profile/<int:user_id>/', views.public_profile, name='public_profile'),

    path('profile/edit/', views.edit_profile, name='edit_profile'),

    path('logout/', views.logout_view, name='logout'),

    path('games/', views.games, name='games'),

    path('games/sprint/', views.game_sprint, name='game_sprint'),

    path('games/falling/', views.game_falling, name='game_falling'),

    path('games/falling-words/', views.game_falling_words, name='game_falling_words'),

    path('games/reaction/', views.game_reaction, name='game_reaction'),

]
