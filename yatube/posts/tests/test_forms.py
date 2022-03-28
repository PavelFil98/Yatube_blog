from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post
from posts.tests import test_constant as const


class FormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_get = get_user_model()
        cls.group = Group.objects.create(
            slug=const.SLUG,
        )
        cls.user = cls.user_get.objects.create_user(username=const.USERNAME)
        cls.post = Post.objects.create(
            text=const.TEXT,
            author=cls.user,
            group=cls.group,
        )
        cls.posts_profile = reverse('posts:profile',
                                    kwargs={'username': cls.user})
        cls.posts_edit = reverse('posts:post_edit',
                                 kwargs={'post_id': cls.post.pk})
        cls.posts_detail = reverse('posts:post_detail',
                                   kwargs={'post_id': cls.post.pk})
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_new_obj_and_redirects(self):
        post_count = Post.objects.count()
        form_data = {
            'text': const.TEXT,
            'group': self.group,
        }
        response = self.authorized_client.post(
            const.POST_CREATE,
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                text=const.TEXT,
                author=self.user,
                group=self.group,
            ).order_by('id')[0]
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertRedirects(response, self.posts_profile)

    def test_edit_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': const.TEXT,
            'group': self.group,

        }
        response = self.authorized_client.post(
            self.posts_edit,
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            self.posts_detail)

        self.assertEqual(Post.objects.count(), post_count)
