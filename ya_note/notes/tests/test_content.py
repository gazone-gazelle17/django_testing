from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestHomePage(TestCase):

    HOME_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(
            username='Тестовый пользователь-автор')
        cls.reader = User.objects.create(
            username='Тестовый пользователь-читатель')
        all_notes_author = [
            Note(
                title=f'Новость {index}',
                text='Просто текст.',
                author=cls.author,
                slug=f'Slug-{index}'
            )
            for index in range(1, 11)
        ]
        all_notes_reader = [
            Note(
                title=f'Новость {index}',
                text='Просто текст.',
                author=cls.reader,
                slug=f'Slug-{index}'
            )
            for index in range(1, 11)
        ]
        Note.objects.bulk_create(all_notes_author + all_notes_reader)

    def test_notes_count(self):
        self.client.force_login(self.reader)
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        object_amount = len(object_list)
        self.assertEqual(object_amount, 10)

    def test_note_create_page_contains_form(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('form', response.context)

    def test_note_edit_page_contains_form(self):
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=[self.note.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('form', response.context)

    def test_note_author(self):
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        notes = response.context['object_list']
        for note in notes:
            self.assertEqual(note.author, self.author)
