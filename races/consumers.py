import asyncio

import json

from urllib.parse import parse_qs

from asgiref.sync import sync_to_async

from channels.generic.websocket import AsyncWebsocketConsumer

from django.utils import timezone

from .achievements import get_unlocked_skins, evaluate_achievements

from .models import RaceResult, RaceRoom, UserProfile

ROOM_STATE = {}

def empty_state():

    return {

        'players': {},

        'started': False,

        'countdown': False,

        'countdown_remaining': 0,

        'finished': False,

        'winner': '',

        'results_sent': False,

        'owner_id': '',

        'delete_task': None,

    }

class RaceConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.code = self.scope['url_route']['kwargs']['code'].upper()

        self.group_name = f'race_{self.code}'

        qs = parse_qs(self.scope.get('query_string', b'').decode())

        self.player_name = qs.get('name', ['Игрок'])[0][:40] or 'Игрок'

        all_skins = {'car_01','car_02','car_03','car_04','car_05','car_06','car_07','car_08','car_09','car_10','car_11','cyber_01','cyber_02','cyber_03','cyber_04','cyber_05','cyber_06','cyber_07','cyber_08','cyber_09','cyber_10'}

        self.skin = qs.get('skin', ['car_01'])[0]

        old_skin_map = {'red': 'car_01', 'blue': 'car_02', 'green': 'car_04', 'yellow': 'car_03', 'purple': 'car_07'}

        self.skin = old_skin_map.get(self.skin, self.skin)

        unlocked_skins = await self.get_unlocked_skins_for_user()

        if self.skin not in all_skins or self.skin not in unlocked_skins:

            self.skin = 'car_01'

        self.player_id = self.channel_name

        try:

            self.room = await sync_to_async(RaceRoom.objects.select_related('text').get)(code=self.code)

        except RaceRoom.DoesNotExist:

            await self.close(code=4404)

            return

        state = ROOM_STATE.setdefault(self.code, empty_state())

        if self.room.status == 'countdown':

            state['countdown'] = True

        if self.room.status == 'running':

            state['started'] = True

        if self.room.status == 'finished':

            state['finished'] = True

        self.is_spectator = state['started'] or state['countdown'] or state['finished'] or self.room.status != 'waiting'

        if not state.get('owner_id') and not self.is_spectator:

            state['owner_id'] = self.player_id

        self.is_owner = state.get('owner_id') == self.player_id

        user = self.scope.get('user')

        can_open_profile = bool(getattr(user, 'is_authenticated', False))

        state['players'][self.player_id] = {

            'id': self.player_id,

            'name': self.player_name,

            'user_id': user.id if can_open_profile else None,

            'profile_url': f'/profile/{user.id}/' if can_open_profile else '',

            'progress': 0,

            'wpm': 0,

            'accuracy': 100,

            'errors': 0,

            'finished': False,

            'spectator': self.is_spectator,

            'skin': self.skin,

            'owner': self.is_owner,

        }

        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

        await self.send_state()

        await self.broadcast_state()

    async def disconnect(self, close_code):

        state = ROOM_STATE.get(self.code)

        if state:

            state['players'].pop(self.player_id, None)

            if state.get('owner_id') == self.player_id:

                active = [pid for pid, p in state['players'].items() if not p.get('spectator')]

                state['owner_id'] = active[0] if active else ''

                if state['owner_id'] in state['players']:

                    state['players'][state['owner_id']]['owner'] = True

            if not state['players'] and not state.get('finished'):

                task = state.get('delete_task')

                if not task or task.done():

                    state['delete_task'] = asyncio.create_task(self.delete_empty_room_later())

        await self.channel_layer.group_discard(self.group_name, self.channel_name)

        await self.broadcast_state()

    async def receive(self, text_data):

        data = json.loads(text_data)

        action = data.get('action')

        state = ROOM_STATE.get(self.code)

        if not state or state['finished']:

            return

        if action == 'start':

            if self.player_id != state.get('owner_id') or self.is_spectator or state['started'] or state['countdown']:

                return

            asyncio.create_task(self.start_countdown())

            return

        if action == 'progress':

            if self.is_spectator or state.get('countdown') or not state['started']:

                return

            player = state['players'].get(self.player_id)

            if not player or player.get('finished'):

                return

            player['progress'] = max(0, min(100, int(data.get('progress', 0))))

            player['wpm'] = max(0, int(data.get('wpm', 0)))

            player['accuracy'] = float(data.get('accuracy', 100))

            player['errors'] = max(0, int(data.get('errors', 0)))

            player['finished'] = bool(data.get('finished', False))

            if player['finished']:

                player['progress'] = 100

                if not state['winner']:

                    state['winner'] = player['name']

                    player['is_win'] = True

                else:

                    player['is_win'] = False

                await self.save_result(player)

            await self.maybe_finish_race()

            await self.broadcast_state()

    async def start_countdown(self):

        state = ROOM_STATE.get(self.code)

        if not state or state.get('started') or state.get('finished') or state.get('countdown'):

            return

        state['countdown'] = True

        state['countdown_remaining'] = 10

        await self.set_room_countdown()

        await self.broadcast_state()

        for remaining in range(10, 0, -1):

            state = ROOM_STATE.get(self.code)

            if not state or state.get('finished'):

                return

            state['countdown_remaining'] = remaining

            await self.channel_layer.group_send(self.group_name, {

                'type': 'countdown_tick',

                'remaining': remaining,

            })

            await self.broadcast_state()

            await asyncio.sleep(1)

        state = ROOM_STATE.get(self.code)

        if not state or state.get('finished'):

            return

        state['countdown'] = False

        state['countdown_remaining'] = 0

        state['started'] = True

        await self.set_room_started()

        await self.channel_layer.group_send(self.group_name, {'type': 'race_started'})

        await self.broadcast_state()

    async def maybe_finish_race(self):

        state = ROOM_STATE[self.code]

        active_players = [p for p in state['players'].values() if not p.get('spectator')]

        if active_players and all(p.get('finished') for p in active_players):

            state['finished'] = True

            await self.set_room_finished(state['winner'])

            await self.channel_layer.group_send(self.group_name, {'type': 'race_finished'})

            asyncio.create_task(self.delete_room_later())

    async def delete_room_later(self):

        await asyncio.sleep(8)

        await self.delete_room_from_db()

        ROOM_STATE.pop(self.code, None)

        await self.channel_layer.group_send(self.group_name, {'type': 'room_deleted'})

    async def delete_empty_room_later(self):

        await asyncio.sleep(6)

        state = ROOM_STATE.get(self.code)

        if state and not state.get('players') and not state.get('finished'):

            await self.delete_room_from_db()

            ROOM_STATE.pop(self.code, None)

    async def send_state(self):

        state = ROOM_STATE[self.code]

        await self.send(text_data=json.dumps({

            'type': 'state',

            'code': self.code,

            'text': self.room.text.content,

            'book': self.room.text.title,

            'author': self.room.text.author,

            'source': self.room.text.source,

            'started': state['started'],

            'countdown': state.get('countdown', False),

            'countdownRemaining': state.get('countdown_remaining', 0),

            'finished': state['finished'],

            'winner': state['winner'],

            'youAreSpectator': self.is_spectator,

            'isOwner': state.get('owner_id') == self.player_id,

            'yourId': self.player_id,

            'players': list(state['players'].values()),

            'results': await self.get_results(),

        }, ensure_ascii=False))

    async def broadcast_state(self):

        await self.channel_layer.group_send(self.group_name, {'type': 'state_changed'})

    async def state_changed(self, event):

        if self.code in ROOM_STATE:

            await self.send_state()

    async def countdown_tick(self, event):

        await self.send(text_data=json.dumps({

            'type': 'countdown',

            'remaining': event.get('remaining', 0),

        }, ensure_ascii=False))

    async def race_started(self, event):

        if not self.is_spectator:

            await self.send(text_data=json.dumps({'type': 'start'}, ensure_ascii=False))

        await self.send_state()

    async def race_finished(self, event):

        await self.send(text_data=json.dumps({'type': 'finish'}, ensure_ascii=False))

        await self.send_state()

    async def room_deleted(self, event):

        await self.send(text_data=json.dumps({

            'type': 'deleted',

            'message': 'Гонка завершена, комната удалена. Результаты сохранены в таблице лидеров.',

        }, ensure_ascii=False))

        await self.close()

    @sync_to_async

    def set_room_countdown(self):

        self.room.status = 'countdown'

        self.room.save(update_fields=['status'])

    @sync_to_async

    def set_room_started(self):

        self.room.status = 'running'

        self.room.started_at = timezone.now()

        self.room.save(update_fields=['status', 'started_at'])

    @sync_to_async

    def set_room_finished(self, winner_name):

        self.room.status = 'finished'

        self.room.winner_name = winner_name

        self.room.save(update_fields=['status', 'winner_name'])

    @sync_to_async

    def save_result(self, player):

        result, created = RaceResult.objects.get_or_create(

            room=self.room,

            player_name=player['name'],

            defaults={

                'wpm': player['wpm'],

                'accuracy': player['accuracy'],

                'errors': player['errors'],

                'is_win': bool(player.get('is_win', False)),

                'user': self.scope.get('user') if getattr(self.scope.get('user'), 'is_authenticated', False) else None,

            },

        )

        if created and result.user:

            evaluate_achievements(result.user, result)

            profile, _ = UserProfile.objects.get_or_create(user=result.user)

            profile.crystals += 10

            profile.save(update_fields=['crystals', 'updated_at'])

    @sync_to_async

    def get_unlocked_skins_for_user(self):

        user = self.scope.get('user')

        return set(get_unlocked_skins(user))

    @sync_to_async

    def get_results(self):

        return list(

            RaceResult.objects.filter(room=self.room)

            .order_by('-wpm', '-accuracy', 'errors')

            .values('player_name', 'wpm', 'accuracy', 'errors', 'user_id')

        )

    @sync_to_async

    def delete_room_from_db(self):

        RaceRoom.objects.filter(pk=self.room.pk).delete()
