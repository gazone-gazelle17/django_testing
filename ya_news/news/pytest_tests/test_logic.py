import pytest

from django.urls import reverse

from pytest_django.asserts import assertRedirects

from http import HTTPStatus

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        client, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        author_client, author, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    url_with_anchor = url + '#comments'
    response = author_client.post(url, form_data)
    assertRedirects(response, url_with_anchor)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.news == form_data['news']
    assert new_comment.author == author
    assert new_comment.text == form_data['text']


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Текст с некрасивыми словами, {BAD_WORDS[0]}'}
    response = author_client.post(url, data=bad_words_data)
    form_errors = response.context['form'].errors
    assert 'text' in form_errors
    assert WARNING in form_errors['text']
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_delete_comment(comment, author_client):
    url = reverse('news:delete', args=(comment.news.id,))
    response = author_client.post(url)
    news_url = reverse('news:detail', args=(comment.news.id,))
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(admin_client, news):
    url = reverse('news:delete', args=(news.id,))
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client, news, form_data, comment):
    url = reverse('news:edit', args=(news.id,))
    response = author_client.post(url, form_data)
    news_url = reverse('news:detail', args=(comment.news.id,))
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.news == form_data['news']
    assert comment.author == form_data['author']
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(admin_client,
                                                form_data, comment, news):
    url = reverse('news:edit', args=(news.id,))
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    actual_comment = Comment.objects.get(id=comment.id)
    assert comment.news == actual_comment.news
    assert comment.author == actual_comment.author
    assert comment.text == actual_comment.text
    assert comment.created == actual_comment.created
