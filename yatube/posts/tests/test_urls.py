from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Group, Post
from posts.tests import test_constant as const


class StaticURLTests(TestCase):
    def test_homepage(self):
        guest_client = Client()
        response = guest_client.get(const.MAIN_PAGE)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_get = get_user_model()
        group = Group.objects.create(
            slug='test-slug',
        )
        user = cls.user_get.objects.create_user(username='user')
        cls.post = Post.objects.create(
            text='',
            author=user,
            group=group,
        )
        cls.post_detail = '/posts/%d/' % cls.post.pk
        cls.post_edit = '/posts/%d/edit/' % cls.post.pk

    def setUp(self):
        self.guest_client = Client()
        self.user = self.user_get.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_url(self):
        '''Страница / доступна любому пользователю.'''
        response = self.guest_client.get(const.MAIN_PAGE)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexiting_page(self):
        response = self.guest_client.get(const.UNEXTING_PAGE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_group_slug(self):
        '''Страница /group/test-slug/ доступна любому пользователю.'''
        response = self.guest_client.get(const.GROUP_LIST)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def tests_profile_username(self):
        '''Страница /profile/StasBasov/ доступна любому пользователю.'''
        response = self.guest_client.get(const.PROFILE)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_id(self):
        response = self.guest_client.get(self.post_detail)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create(self):
        '''Страница /create/ доступна авторизованному пользователю.'''
        response = self.authorized_client.get(const.CREATE)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_id_edit(self):
        '''Страница /posts/id/edit доступна авторизованному пользователю.'''
        response = self.guest_client.get(self.post_edit,
                                         follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/posts/%d/edit/' % self.post.pk)

    def test_urls_uses_correct_template(self):
        '''URL-адрес использует соответствующий шаблон.'''
        templates_url_names = {
            const.MAIN_PAGE: const.MAIN_PAGE_HTML,
            const.GROUP_LIST: const.GROUP_LIST_HTML,
            const.PROFILE: const.PROFILE_HTML,
            self.post_detail: const.POST_DETAIL_HTML,
            const.CREATE: const.CREATE_HTML,
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.post(url)
                self.assertTemplateUsed(response, template)
