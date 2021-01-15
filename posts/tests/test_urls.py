from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Лучшие',
            slug='best',
            description='Лучшая группа в мире..',
        )
        cls.user = User.objects.create(username='hulk')
        cls.post = Post.objects.create(
            pk=0,
            text='123456789012345_Меня не должно быть видно :):)',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)

    def test_posts_url_exists_at_desired_location_authorized(self):
        slug = PostsURLTests.group.slug
        username = PostsURLTests.user.username
        post_id = PostsURLTests.post.id
        urls_list_authorized = [
            reverse('posts:index'),
            reverse('posts:group', kwargs={'slug': slug}),
            reverse('posts:new_post'),
            reverse('posts:profile', kwargs={'username': username}),
            reverse('posts:post', kwargs={'username': username,
                                          'post_id': post_id}),
            reverse('posts:follow_index'),
            reverse('posts:add_comment', kwargs={'username': username,
                                                 'post_id': post_id}),
            reverse('posts:post_edit',
                    kwargs={'username': username, 'post_id': post_id}),
        ]
        for url in urls_list_authorized:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)  # noqa
                self.assertEqual(
                    response.status_code,
                    200,
                    f'Страница {url} недоступна'
                )

    def test_posts_url_exists_at_desired_location_anonymous(self):
        slug = PostsURLTests.group.slug
        username = PostsURLTests.user.username
        post_id = PostsURLTests.post.id
        urls_list_anonymous = [
            reverse('posts:index'),
            reverse('posts:group', kwargs={'slug': slug}),
            reverse('posts:profile', kwargs={'username': username}),
            reverse('posts:post', kwargs={'username': username,
                                          'post_id': post_id}),
        ]
        for url in urls_list_anonymous:
            with self.subTest(url=url):
                response = self.guest_client.get(url)  # noqa
                self.assertEqual(
                    response.status_code,
                    200,
                    f'Страница {url} недоступна'
                )

    def test_posts_redirect_anonymous_auth_login(self):
        username = PostsURLTests.user.username
        post_id = PostsURLTests.post.id
        url_list = [
            reverse('posts:new_post'),
            reverse('posts:post_edit',
                    kwargs={'username': username, 'post_id': post_id}),
            reverse('posts:follow_index'),
            reverse('posts:profile_follow', kwargs={'username': username}),
            reverse('posts:profile_unfollow', kwargs={'username': username}),
            reverse('posts:add_comment',
                    kwargs={'username': username, 'post_id': post_id}),

        ]
        for url in url_list:
            with self.subTest():
                response = self.guest_client.get(url)  # noqa
                self.assertRedirects(
                    response,
                    reverse('login') + f'?next={url}',
                    302,
                    200,
                    'Неверный редирект для анонимного пользователя'
                )

    def test_posts_urls_uses_correct_template(self):
        slug = PostsURLTests.group.slug
        username = PostsURLTests.user.username
        post_id = PostsURLTests.post.id
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
            with self.subTest():
                response = self.authorized_client.get(reverse_name)  # noqa
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Неверный шаблон страницы {reverse_name}'
                )

    def test_posts_urls_post_edit_url_not_author(self):
        username = PostsURLTests.user.username
        post_id = PostsURLTests.post.id
        new_user = User.objects.create(username='admin')
        auth_client_user_not_post_author = Client()
        auth_client_user_not_post_author.force_login(new_user)
        url = reverse('posts:post_edit',
                      kwargs={'username': username, 'post_id': post_id})
        response = auth_client_user_not_post_author.get(url, follow=True)  # noqa
        self.assertRedirects(
            response,
            reverse('posts:post',
                    kwargs={'username': username, 'post_id': post_id}),
            302,
            200,
            'Неверный редирект для авторизированного пользователя (не автор)'
        )

    def test_posts_page_not_exists_returns_404(self):
        response = self.authorized_client.get('/i_am_does_not_exist/')  # noqa
        self.assertEqual(
            response.status_code,
            404,
            'Возвращен неверный код несуществующей страницы. Должен быть 404'
        )
