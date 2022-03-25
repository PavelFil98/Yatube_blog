from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_get = get_user_model()
        cls.user = cls.user_get.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        expected_object_name = 'Тестовая пост'
        self.assertEqual(expected_object_name, str(self.post))
        expected_object_name_group = 'Тестовая группа'
        self.assertEqual(expected_object_name_group, str(self.group))
