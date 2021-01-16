from datetime import datetime as dt

from django.urls import reverse
from django.test import TestCase, Client

from posts.models import Post, User


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='hulk')

        for post in range(13):
            Post.objects.create(
                text='Тестовая страница ' + str(post),
                pub_date=dt.today,
                author=cls.user,
            )

    def setUp(self):
        self.guest_client = Client()

    def test_posts_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context.get('page').object_list),
            10,
            'Неверное количество постов на первой странице, корректное - 10'
        )

    def test_posts_second_page_contains_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(
            len(response.context.get('page').object_list),
            3,
            'Неверное количество постов на второй странице, корректное - 3'
        )

    def test_posts_second_page_show_correct_context(self):
        response = self.guest_client.get(reverse('posts:index'))
        post_text_2 = response.context.get('page')[2].text
        self.assertEqual(
            post_text_2,
            'Тестовая страница 10',
            'Нверный контекст поста на второй странице'
        )
