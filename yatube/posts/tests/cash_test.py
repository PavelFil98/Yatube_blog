from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client
from posts.models import Group, Post
from posts.tests import test_constant as const

User = get_user_model()


class CacheTest(TestCase):
    """Проверяем, что кешируется главная страница"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.group = Group.objects.create(
            title='test',
            slug='test',
            description='test'
        )
        cls.post = Post.objects.create(
            text='post',
            group=cls.group,
            author=cls.author
        )

    def test_cache_index(self):
        response = self.authorized_client.get(const.POSTS_INDEX)
        posts = response.content
        Post.objects.create(
            text='post',
            author=self.author,
        )
        response_old = self.authorized_client.get(const.POSTS_INDEX)

        old_posts = response_old.content
        self.assertEqual(
            old_posts,
            posts,
        )
        cache.clear()
        response_new = self.authorized_client.get(const.POSTS_INDEX)
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts, )
