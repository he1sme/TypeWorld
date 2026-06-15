from django.urls import re_path

from . import consumers

websocket_urlpatterns = [

    re_path(r'ws/room/(?P<code>[A-Z0-9]+)/$', consumers.RaceConsumer.as_asgi()),

]
