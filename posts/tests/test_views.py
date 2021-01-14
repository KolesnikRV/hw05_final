from datetime import datetime as dt
import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.forms import fields
from django.test import TestCase, Client, override_settings

from posts.models import Post, Group, User

MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
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
        image = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                 b'\x01\x00\x80\x00\x00\x00\x00\x00'
                 b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                 b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                 b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                 b'\x0A\x00\x3B')
        uploaded = SimpleUploadedFile(
            name='image.gif',
            content=image,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            pk=0,
            text='Тестовая страница',
            pub_date=dt.today,
            author=cls.user,
            group=cls.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsViewsTests.user)

    def test_pages_uses_correct_template(self):
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
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Неверный шаблон страницы {reverse_name}'
                )

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        post_context_0 = response.context.get('page')[0]
        self.assertEqual(
            post_context_0,
            PostsViewsTests.post,
            'Неверный контекст на главной странице'
        )

    def test_profile_page_show_correct_context(self):
        username = PostsViewsTests.user.username
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': username})
        )
        post_context_0 = response.context.get('page')[0]
        post_count = response.context.get('post_count')
        post_author = response.context.get('author')
        self.assertEqual(
            post_context_0,
            PostsViewsTests.post,
            'Неверный контекст поста на странице профиля пользователя'
        )
        self.assertEqual(
            post_count,
            9,
            'Неверный контекст счетчика постов post_count '
            'на странице профиля пользователя'
        )
        self.assertEqual(
            post_author,
            PostsViewsTests.user,
            'Неверный контекст автор на странице профиля пользователя'
        )

    def test_post_page_show_correct_context(self):
        username = PostsViewsTests.user.username
        post_id = PostsViewsTests.post.id
        response = self.authorized_client.get(
            reverse('posts:post', kwargs={'username': username,
                                          'post_id': post_id})
        )
        post_context = response.context.get('post')
        post_count = response.context.get('post_count')
        post_author = response.context.get('author')
        self.assertEqual(
            post_context,
            PostsViewsTests.post,
            'Неверный контекст поста на странице просмотра отдельного поста'
        )
        self.assertEqual(
            post_count,
            9,
            'Неверный контекст счетчика постов post_count '
            'на странице просмотра отдельного поста'
        )
        self.assertEqual(
            post_author,
            PostsViewsTests.user,
            'Неверный контекст автор на странице просмотра отдельного поста'
        )

    def test_post_edit_page_show_correct_context(self):
        username = PostsViewsTests.user.username
        post_id = PostsViewsTests.post.id
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'username': username, 'post_id': post_id})
        )
        form_fields = {
            'text': fields.CharField,
            'group': fields.ChoiceField,
        }
        for field, expected in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get('form').fields.get(field)
                self.assertIsInstance(
                    form_field,
                    expected,
                    f'Неверный контекст формы для поля {field}'
                )

        post_context = response.context.get('post')
        self.assertEqual(
            post_context,
            PostsViewsTests.post,
            'Неверный контекст поста на странице редактирования поста'
        )

    def test_group_page_show_correct_context(self):
        slug = PostsViewsTests.group.slug
        response = self.authorized_client.get(
                reverse('posts:group', kwargs={'slug': slug})
        )
        group_context = response.context.get('group')
        self.assertEqual(
            group_context,
            PostsViewsTests.group,
            'Неверный контекст группы на странице группы'
        )

    def test_new_post_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:new_post'))
        form_fields = {
            'text': fields.CharField,
            'group': fields.ChoiceField,
        }
        for field, expected in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get('form').fields.get(field)
                self.assertIsInstance(
                    form_field,
                    expected,
                    f'Неверный контекст формы для поля {field}'
                )

    def test_index_page_posts_count_is_9(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context['page']),
            9,
            'Неверное количество постов на главной странице'
        )

    def test_group_page_post_is_in_right_group(self):
        slug = PostsViewsTests.group.slug
        response = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': slug})
        )
        self.assertEqual(
            len(response.context['page']),
            1,
            f'Пост отсутствует в группе {slug}'
        )

    def test_group_page_post_not_in_another_group(self):
        group = Group.objects.create(
            title='Худшие',
            slug='worst',
            description='Худшая группа в мире..',
        )
        Post.objects.create(author=PostsViewsTests.user)
        response = self.authorized_client.get(reverse('posts:group',
                                              kwargs={'slug': group.slug}))
        self.assertEqual(
            len(response.context['page']),
            0,
            'Пост попал не в ту группу'
        )

    def test_idex_page_cache(self):
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

    def test_first_page_containse_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context.get('page').object_list),
            10,
            'Неверное количество постов на первой странице, корректное - 10'
        )

    def test_second_page_containse_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(
            len(response.context.get('page').object_list),
            3,
            'Неверное количество постов на второй странице, корректное - 3'
        )

    def test_second_page_show_correct_context(self):
        response = self.guest_client.get(reverse('posts:index'))
        post_text_2 = response.context.get('page')[2].text
        self.assertEqual(
            post_text_2,
            'Тестовая страница 10',
            'Нверный контекст поста на второй странице'
        )
