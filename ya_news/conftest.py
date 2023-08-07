from datetime import datetime
import pytest

from django.conf import settings

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст записи',
        date=datetime.today().date(),
    )
    return news


@pytest.fixture
def create_news_objects():
    news_list = [
        News(
            title=f'Заголовок #{i}',
            text=f'Текст записи #{i}',
            date=datetime.today().date(),
        )
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE)
    ]
    News.objects.bulk_create(news_list)
    return news_list


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
        created=datetime.now(),
    )


@pytest.fixture
def form_data(news, author):
    return {
        'news': news,
        'author': author,
        'text': 'Новый комментарий',
        'created': datetime.now(),
    }
