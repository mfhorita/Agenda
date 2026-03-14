from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from app.models import Evento


class EventoSecurityTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='senha12345')
        self.other_user = User.objects.create_user(username='other', password='senha12345')

        self.owner_event = Evento.objects.create(
            titulo='Evento privado',
            descricao='descricao',
            data_evento=timezone.now() + timedelta(days=1),
            usuario=self.owner,
        )

    def test_evento_view_blocks_access_to_other_users_event(self):
        self.client.login(username='other', password='senha12345')

        response = self.client.get(f'/agenda/evento/?id={self.owner_event.id}')

        self.assertEqual(response.status_code, 404)

    def test_json_lista_evento_blocks_access_to_other_users_id(self):
        self.client.login(username='other', password='senha12345')

        response = self.client.get(f'/agenda/lista/{self.owner.id}/')

        self.assertEqual(response.status_code, 404)

    def test_json_lista_evento_returns_only_authenticated_user_events(self):
        Evento.objects.create(
            titulo='Outro evento',
            descricao='descricao',
            data_evento=timezone.now() + timedelta(days=1),
            usuario=self.other_user,
        )
        self.client.login(username='other', password='senha12345')

        response = self.client.get(f'/agenda/lista/{self.other_user.id}/')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]['titulo'], 'Outro evento')
