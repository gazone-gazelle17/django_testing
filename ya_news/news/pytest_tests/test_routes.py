import pytest

from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture


@pytest.mark.parametrize(
    'name, comment_object',
    (
        ('news:edit', lazy_fixture('comment')),
        ('news:delete', lazy_fixture('comment'))
    ),
)
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (lazy_fixture('author_client'), HTTPStatus.OK)
    )
)
def test_availability_for_comment_and_delete(
        parametrized_client, name, comment_object, expected_status
):
    url = reverse(name, args=(comment_object.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, news_object',
    (
        ('news:home', None),
        ('news:detail', lazy_fixture('news')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ),
)
@pytest.mark.django_db
def test_pages_availability_for_different_users(
    name, news_object, client
):
    if news_object is not None:
        url = reverse(name, args=(news_object.id,))
    else:
        url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name, comment_obj',
    (
        ('news:edit', lazy_fixture('comment')),
        ('news:delete', lazy_fixture('comment'))
    )
)
@pytest.mark.django_db
def test_redirect_for_anonymous_user(
    client, name, comment_obj
):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment_obj.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
