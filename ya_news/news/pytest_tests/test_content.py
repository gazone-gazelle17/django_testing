import pytest

from django.urls import reverse
from pytest_lazyfixture import lazy_fixture


@pytest.mark.django_db
def test_news_count_and_order(client, create_news_objects):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) == len(create_news_objects)
    dates = [news.date for news in object_list]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.parametrize(
    'name, news_object',
    (
        ('news:detail', lazy_fixture('news')),
    )
)
@pytest.mark.django_db
def test_comments_order(client, name, news_object):
    url = reverse(name, args=(news_object.id,))
    response = client.get(url)
    comment_list = response.context['news'].comment_set.all()
    comments = [comment.created for comment in comment_list]
    sorted_comments = sorted(comments)
    assert comments == sorted_comments


@pytest.mark.parametrize(
    'parametrized_client, expected_response',
    (
        (lazy_fixture('client'), False),
        (lazy_fixture('admin_client'), True)
    )
)
@pytest.mark.parametrize(
    'name, comment_object',
    (
        ('news:detail', lazy_fixture('comment')),
    )
)
@pytest.mark.django_db
def test_form_is_shown_appropriate(
    parametrized_client, name, comment_object, expected_response
):
    url = reverse(name, args=(comment_object.id,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) == expected_response
