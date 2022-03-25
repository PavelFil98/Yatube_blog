from http import HTTPStatus

from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse
from posts.models import Group, Post, Follow
from posts.tests import test_constant as const

User = get_user_model()


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            slug=const.SLUG,
        )
        cls.user_user = User.objects.create_user(username='User')
        cls.post = Post.objects.create(
            text='',
            author=cls.user_user,
            group=cls.group,
        )
        cls.posts_detail = reverse('posts:post_detail',
                                   kwargs={'post_id': cls.post.pk})
        cls.posts_edit = reverse('posts:post_edit',
                                 kwargs={'post_id': cls.post.pk})
        cls.posts_profile = reverse('posts:profile',
                                    kwargs={'username': cls.user_user})

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username=const.USERNAME)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        '''URL-адрес использует соответствующий шаблон.'''
        templates_page_names = {
            const.POSTS_INDEX: const.MAIN_PAGE_HTML,
            const.POST_GROUP_LIST: const.GROUP_LIST_HTML,
            const.POSTS_PROFILE: const.PROFILE_HTML,
            self.posts_detail: const.POST_DETAIL_HTML,
            const.POST_CREATE: const.CREATE_HTML,

        }

        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.post(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_group_list_page_show_correct_context(self):
        response = self.authorized_client.get(const.POST_GROUP_LIST)
        self.assertEqual(
            response.context.get('page_obj')[0].text, ''
        )

    def test_profile_page_show_correct_context(self):
        response = self.client.get(self.posts_profile)
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        task_author_0 = first_object.author
        self.assertEqual(task_text_0, '')
        self.assertEqual(task_author_0, self.user_user)

    def test_post_detail_page_show_correct_context(self):
        response = self.client.get(self.posts_detail)
        first_object = response.context['posts']
        task_id = first_object.id
        self.assertEqual(task_id, self.post.pk)

    def test_create_post_page_show_correct_context(self):
        response = self.authorized_client.get(const.POST_CREATE)
        form_fields = {
            'text': forms.fields.CharField,

        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_3_index(self):
        response = self.authorized_client.get(const.POSTS_INDEX)
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        task_group_0 = first_object.group.title
        self.assertEqual(task_text_0, '')
        self.assertEqual(task_group_0, '')

    def test_3_grop_list(self):
        response = self.authorized_client.get(const.POST_GROUP_LIST)
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        task_group_0 = first_object.group.title
        self.assertEqual(task_text_0, '')
        self.assertEqual(task_group_0, '')

    def test_3_profile(self):
        response = self.authorized_client.get(self.posts_profile)
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        task_group_0 = first_object.group.title
        self.assertEqual(task_text_0, '')
        self.assertEqual(task_group_0, '')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        group = Group.objects.create(
            slug=const.SLUG,
        )
        user = User.objects.create_user(username='user')
        for i in range(13):
            Post.objects.create(
                text='',
                author=user,
                group=group,
            )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='User')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_first_page_contains_ten_records(self):
        response = self.client.get(const.POSTS_INDEX)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_three_records(self):
        response = self.client.get(const.POSTS_INDEX + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_first_page_contains_ten_records(self):
        response = self.client.get(const.POST_GROUP_LIST)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_second_page_contains_three_records(self):
        response = self.client.get(const.POST_GROUP_LIST + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_first_page_contains_ten_records(self):
        response = self.client.get(const.POSTS_PROFILE)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_second_page_contains_three_records(self):
        response = self.client.get(const.POSTS_PROFILE + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)


class CacheTest(TestCase):
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


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.author = User.objects.create_user(
            username='test_author'
        )
        cls.auth_author_client = Client()
        cls.auth_author_client.force_login(cls.author)

        cls.user_fol = User.objects.create_user(
            username='test_user_fol'
        )
        cls.authorized_user_fol_client = Client()
        cls.authorized_user_fol_client.force_login(
            cls.user_fol
        )

        cls.user_unfol = User.objects.create_user(
            username='test_user_unfol'
        )
        cls.authorized_user_unfol_client = Client()
        cls.authorized_user_unfol_client.force_login(
            cls.user_unfol
        )
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-slug',
            description='test_description'
        )
        cls.post = Post.objects.create(
            text='test_post',
            group=cls.group,
            author=cls.author
        )

    def test_follow(self):
        client = self.authorized_user_unfol_client
        user = self.user_unfol
        author = self.author
        client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author}
            )
        )
        follower = Follow.objects.filter(
            user=user,
            author=author
        ).exists()
        self.assertTrue(
            follower,
        )

    def test_unfollow(self):
        client = self.authorized_user_unfol_client
        user = self.user_unfol
        author = self.author
        client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.author}
            ),

        )
        follower = Follow.objects.filter(
            user=user,
            author=author
        ).exists()
        self.assertFalse(
            follower,
        )


class CommentTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

        cls.auth_user = User.objects.create_user(
            username='test_auth_user'
        )

        cls.author = User.objects.create_user(
            username='test_author'
        )

        cls.group = Group.objects.create(
            title='test_group',
            slug='test-slug',
            description='test_description'
        )

        cls.post = Post.objects.create(
            text='test_post',
            group=cls.group,
            author=cls.author
        )

    def test_comment_guest(self):
        response = self.guest_client.get(
            reverse(
                'posts:add_comment',
                kwargs={
                    'post_id': self.post.pk
                }
            )
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.FOUND,
        )
