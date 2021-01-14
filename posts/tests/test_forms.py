import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from posts.forms import PostForm, CommentForm
from posts.models import Post, User, Comment

MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='hulk')
        Post.objects.create(
            pk=0,
            text='Тестовая страница',
            author=cls.user,
        )
        cls.image = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B')
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)
        self.uploaded = SimpleUploadedFile(
            name='image.gif',
            content=PostFormTests.image,
            content_type='image/gif'
        )

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый Текст',
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:index'),
            302,
            200,
            'Неверный редирект после создания поста'
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count + 1,
            'Неверное количество записей в БД после создания нового поста'
        )

    def test_edit_post(self):
        post = Post.objects.get(pk=0)
        form_data = {
            'text': 'Новый текст',
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'username': 'hulk', 'post_id': post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post',
                    kwargs={'username': 'hulk', 'post_id': post.id}),
            302,
            200,
            'Неверный редирект после редактирования поста'
        )
        self.assertEqual(
            Post.objects.get(id=0).text,
            'Новый текст',
            'Некорректная работа функции редактирования поста'
        )


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='hulk')
        cls.post = Post.objects.create(
            pk=0,
            text='Тестовая страница',
            author=cls.user,
        )
        Comment.objects.create(
            post=CommentFormTests.post,
            author=CommentFormTests.user,
            text='Первый комментарий',
        )
        cls.form = CommentForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(CommentFormTests.user)

    def test_create_comment(self):
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый Текст',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'username': CommentFormTests.user,
                            'post_id': CommentFormTests.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post',
                    kwargs={'username': CommentFormTests.user,
                            'post_id': CommentFormTests.post.id}),
            302,
            200,
            'Неверный редирект после создания комментария'
        )
        self.assertEqual(
            Comment.objects.count(),
            comments_count + 1,
            'Неверное количество записей в БД '
            'после создания нового комментария'
        )
