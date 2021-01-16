from datetime import datetime as dt

from django.urls import reverse
from django.test import TestCase, Client

from posts.models import Post, Group, User


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Лучшие',
            slug='best',
            description='Лучшая группа в мире..',
        )
        cls.user = User.objects.create(username='hulk')

        for post in range(8):
            Post.objects.create(
                text='Тестовая страница ' + str(post),
                pub_date=dt.today,
                author=cls.user,
            )

        cls.post = Post.objects.create(
            pk=0,
            text='Тестовая страница',
            pub_date=dt.today,
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsViewsTests.user)

    def test_posts_pages_uses_correct_template(self):
        slug = PostsViewsTests.group.slug
        username = PostsViewsTests.user.username
        post_id = PostsViewsTests.post.id
        templates_pages_names = {
            'index.html': reverse('posts:index'),
            'group.html': reverse('posts:group', kwargs={'slug': slug}),
            'posts/post_new.html': reverse('posts:new_post'),
            'profile.html': reverse(
                'posts:profile',
                kwargs={'username': username}
            ),
            'posts/post.html': reverse(
                'posts:post',
                kwargs={'username': username, 'post_id': post_id}
            ),
            'follow.html': reverse('posts:follow_index'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Неверный шаблон страницы {reverse_name}'
                )

    def test_posts_index_page_posts_count_is_9(self):
        posts_in_database = Post.objects.all().count()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context['page']),
            posts_in_database,
            'Неверное количество постов на главной странице'
        )

    def test_posts_idex_page_cache(self):
        response_1 = self.guest_client.get(reverse('posts:index'))
        Post.objects.create(
                text='Тестовая страница ',
                pub_date=dt.today,
                author=PostsViewsTests.user,
        )
        response_2 = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(response_1.content,
                         response_2.content,
                         'Cache не работает')
        Post.objects.create(
                text='Тестовая страница ',
                pub_date=dt.today,
                author=PostsViewsTests.user,
        )
        response_3 = self.guest_client.get(reverse('posts:index') + '?page=2')
        self.assertNotEqual(response_2.content,
                            response_3.content,
                            'Cache не работает, page 2')

    def test_posts_group_page_post_is_in_right_group(self):
        slug = PostsViewsTests.group.slug
        posts_in_group = Post.objects.filter(group__slug=slug).count()
        response = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': slug})
        )
        self.assertEqual(
            len(response.context['page']),
            posts_in_group,
            f'Пост отсутствует в группе {slug}'
        )

    def test_posts_group_page_post_not_in_another_group(self):
        group = Group.objects.create(
            title='Худшие',
            slug='worst',
            description='Худшая группа в мире..',
        )
        Post.objects.create(author=PostsViewsTests.user)
        posts_in_group = Post.objects.filter(group__slug=group.slug).count()
        response = self.authorized_client.get(reverse('posts:group',
                                              kwargs={'slug': group.slug}))
        self.assertEqual(
            len(response.context['page']),
            posts_in_group,
            'Пост попал не в ту группу'
        )

    def test_posts_subscription_unsubscription_for_auth_user(self):
        user1 = User.objects.create(username='user1')
        Post.objects.create(
            text='Пост юзера 1',
            pub_date=dt.today,
            author=user1,
        )
        subscription_count = PostsViewsTests.user.follower.count()
        self.authorized_client.get(reverse('posts:profile_follow',
                                   kwargs={'username': user1}))

        self.assertEqual(
            PostsViewsTests.user.follower.count(),
            subscription_count + 1,
            'Неверная работа функции добавления подписки'
        )
        self.authorized_client.get(reverse('posts:profile_unfollow',
                                   kwargs={'username': user1}))
        self.assertEqual(
            PostsViewsTests.user.follower.count(),
            subscription_count,
            'Неверная работа функции удаления подписки'
        )
