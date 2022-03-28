from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from posts.models import Group, Post, Comment

User = get_user_model()


class CommentPagesTests(TestCase):
    """Проверяем комментарии """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_object = Group.objects.create(
            title='title',
            slug='test-slug',
            description=''
        )

    def setUp(self):
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text='text',
            author=self.user,
            group=CommentPagesTests.group_object,
        )
        self.comment = Comment.objects.create(
            post=self.post,
            text='text',
            author=self.user,
        )

    def test_create_comment(self):
        form_data = {
            'post': self.post,
            'text': 'text',
            'author': self.user,
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        self.assertTrue(Comment.objects.latest('created'))
        self.assertEqual(Comment.objects.latest('created').text,
                         'text'
                         )


class CommentFormTests(TestCase):

    @classmethod
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
        )

    def test_create_comment_form(self):
        """Проверка формы создания нового комментария."""
        author = self.author
        post = self.post
        client = self.auth_user_client
        comments_count = Comment.objects.filter(
            post=post.pk
        ).count()
        form_data = {
            'text': 'test_comment',
        }

        response = client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        comments = Post.objects.filter(
            id=post.pk
        ).values_list('comments', flat=True)
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': post.pk
                }
            )
        )
        self.assertEqual(
            comments.count(),
            comments_count + 1
        )
        self.assertTrue(
            Comment.objects.filter(
                post=post.pk,
                author=self.auth_user.pk,
                text=form_data['text']
            ).exists()
        )
