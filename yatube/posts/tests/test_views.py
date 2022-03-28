from django import forms
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from posts.models import Group, Post, Follow, Comment
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



