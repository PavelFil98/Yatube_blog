import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post
from posts.tests import test_constant as const

User = get_user_model()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
class PostFormTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='testuser')
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.auth_user = User.objects.create_user(
            username='test_auth_user'
        )
        self.auth_user_client = Client()
        self.auth_user_client.force_login(
            self.auth_user
        )
        self.small_gif_old1 = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        self.small_gif_old2 = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        self.small_gif_new = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )

        self.uploaded_old1 = SimpleUploadedFile(
            name='small_old1.gif',
            content=self.small_gif_old1,
            content_type='image/gif'
        )
        self.uploaded_old2 = SimpleUploadedFile(
            name='small_old2.gif',
            content=self.small_gif_old2,
            content_type='image/gif'
        )
        self.uploaded_new = SimpleUploadedFile(
            name='small_new.gif',
            content=self.small_gif_new,
            content_type='image/gif'
        )
        self.group_old = Group.objects.create(
            title='test_group_old',
            slug='test-slug-old',
            description='test_description'
        )
        self.group_new = Group.objects.create(
            title='test_group_new',
            slug='test-slug-new',
            description='test_description'
        )
        self.post = Post.objects.create(
            text='test_post',
            group=self.group_old,
            author=self.author,
            image=self.uploaded_old1
        )
        self.form = PostForm()

    def test_create_post(self):
        """Проверка формы создания нового поста."""
        posts_count = Post.objects.count()
        group_field = self.group_old.id
        form_data = {
            'text': 'test_new_post',
            'group': group_field,
            'image': self.uploaded_old2
        }

        self.author_client.post(
            const.POST_CREATE,
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.group_old.id,
                text='test_new_post',
                image='posts/small_old2.gif',
            ).exists()
        )

    def test_edit_post(self):
        """Проверка формы редактирования поста и изменение
        его в базе данных."""
        group_field_new = self.group_new.id
        form_data = {
            'text': 'test_edit_post',
            'group': group_field_new,
            'image': self.uploaded_new
        }
        response = self.author_client.post(
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': self.post.pk
                }

            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': self.post.pk
                }
            )
        )
        self.assertTrue(
            Post.objects.filter(
                group=self.group_new.id,
                text='test_edit_post',
                image='posts/small_new.gif'
            ).exists()
        )
        self.assertFalse(
            Post.objects.filter(
                group=self.group_old.id,
                text='test_post',
                image='posts/small_old1.gif'
            ).exists()
        )
