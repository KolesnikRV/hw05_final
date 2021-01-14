from django.test import TestCase

from posts.models import Post, Group, User


class PostsModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='hulk')
        cls.post = Post.objects.create(
            pk=0,
            text='123456789012345_Меня не должно быть видно :):)',
            author=cls.user,
        )
        cls.group = Group.objects.create(
            title='Лучшие',
            slug='best',
            description='Лучшая группв в мире..',
        )

    def test_method__str__for_model_post(self):
        post = PostsModelTest.post
        expected_for_post = post.text[:15]

        self.assertEquals(
            expected_for_post,
            str(post),
            'Некорректная работа функции __str__ модели post'
        )

    def test_method__str__for_model_group(self):
        group = PostsModelTest.group
        expected_for_group = group.title

        self.assertEquals(
            expected_for_group,
            str(group),
            'Некорректная работа функции __str__ модели group'
        )

    def test_verbose(self):
        model_field = {
            'text': 'Текст',
            'group': 'Группа',
        }
        for field, text in model_field.items():
            with self.subTest(field=field):
                post = PostsModelTest.post
                verbose_name = post._meta.get_field(field).verbose_name
                self.assertEqual(
                    verbose_name,
                    text,
                    f'Неверный verbose_name для поля {field}'
                )

    def test_help_text(self):
        model_field = {
            'text': ('Введите текст поста.'
                     '<p>* Oбязательно для заполнения.</p>'),
            'group': ('Выберите одну из существующих групп.'
                      '<p>Не обязательно для заполнения.</p>'),
        }
        for field, text in model_field.items():
            with self.subTest(field=field):
                post = PostsModelTest.post
                help_text = post._meta.get_field(field).help_text
                self.assertEqual(
                    help_text,
                    text,
                    f'Неверный help_text для поля {field}'
                )
