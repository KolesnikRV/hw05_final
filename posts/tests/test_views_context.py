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

    def test_posts_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        post_context_0 = response.context.get('page')[0]
        self.assertEqual(
            post_context_0,
            PostsViewsTests.post,
            'Неверный контекст на главной странице'
        )

    def test_posts_profile_page_show_correct_context(self):
        username = PostsViewsTests.user.username
        posts_in_database = Post.objects.all().count()
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': username})
        )
        post_context_0 = response.context.get('page')[0]
        post_count = response.context.get('post_count')
        post_author = response.context.get('author')
        post_following = response.context.get('following')
        self.assertEqual(
            post_context_0,
            PostsViewsTests.post,
            'Неверный контекст поста на странице профиля пользователя'
        )
        self.assertEqual(
            post_count,
            posts_in_database,
            'Неверный контекст счетчика постов post_count '
            'на странице профиля пользователя'
        )
        self.assertEqual(
            post_author,
            PostsViewsTests.user,
            'Неверный контекст автор на странице профиля пользователя'
        )
        self.assertEqual(
            post_following,
            False,
            'Неверный контекст Подписки на странице профиля пользователя'
        )

    def test_posts_post_page_show_correct_context(self):
        username = PostsViewsTests.user.username
        posts_in_database = Post.objects.all().count()
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
            posts_in_database,
            'Неверный контекст счетчика постов post_count '
            'на странице просмотра отдельного поста'
        )
        self.assertEqual(
            post_author,
            PostsViewsTests.user,
            'Неверный контекст автор на странице просмотра отдельного поста'
        )

    def test_posts_edit_page_show_correct_context(self):
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

    def test_posts_group_page_show_correct_context(self):
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

    def test_posts_new_post_page_show_correct_context(self):
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

    def test_posts_subscription_page_show_correct_context(self):
        user_following = User.objects.create(username='user_following')
        user_following_auth = Client()
        user_following_auth.force_login(user_following)
        user_no_subscription = User.objects.create(username='user_no_sub')
        user_no_subscription_auth = Client()
        user_no_subscription_auth.force_login(user_no_subscription)
        user_follower = User.objects.create(username='user_follower')
        user_follower_auth = Client()
        user_follower_auth.force_login(user_follower)

        user_follower_response = user_follower_auth.get(
            reverse('posts:follow_index')
        )
        user_follower_post_count = len(
            user_follower_response.context.get('page').object_list
        )
        user_no_subscription_response = user_no_subscription_auth.get(
            reverse('posts:follow_index')
        )
        user_no_subscription_post_count = len(
            user_no_subscription_response.context.get('page').object_list
        )
        user_follower_auth.get(reverse('posts:profile_follow',
                               kwargs={'username': user_following}))
        Post.objects.create(
            text='Пора выпить чайку',
            pub_date=dt.today,
            author=user_following,
        )
        response = user_follower_auth.get(reverse('posts:follow_index'))
        self.assertEqual(
            len(response.context.get('page').object_list),
            user_follower_post_count + 1,
            'Неверная работа ленты подписок (отсутствует новый пост)'
        )

        response = user_no_subscription_auth.get(reverse('posts:follow_index'))
        self.assertEqual(
            len(response.context.get('page').object_list),
            user_no_subscription_post_count,
            'Неверная работа ленты подписок (лишний новый пост)'
        )
