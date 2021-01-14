from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url_temtemplates_pages_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }

    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_exists_at_desired_location(self):
        url_list = StaticURLTests.url_temtemplates_pages_names.values()
        for url in url_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code,
                    200,
                    f'Страница {url} недоступна'
                )

    def test_about_urls_uses_correct_template(self):
        templates_pages_names = StaticURLTests.url_temtemplates_pages_names
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Неверный шаблон страницы {reverse_name}'
                )
