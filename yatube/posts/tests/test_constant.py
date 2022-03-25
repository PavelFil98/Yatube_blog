from django.urls import reverse

MAIN_PAGE = '/'
MAIN_PAGE_HTML = 'posts/index.html'
GROUP_LIST = '/group/test-slug/'
GROUP_LIST_HTML = 'posts/group_list.html'
PROFILE = '/profile/StasBasov/'
PROFILE_HTML = 'posts/profile.html'
CREATE = '/create/'
CREATE_HTML = 'posts/create_post.html'
POST_DETAIL_HTML = 'posts/post_detail.html'
UNEXTING_PAGE = '/unexting-page'
TEXT = 'Тестовый текст'
SLUG = 'test-slug'
USERNAME = 'user'
POST_CREATE = reverse('posts:post_create')
POSTS_INDEX = reverse('posts:index')
POST_GROUP_LIST = reverse('posts:group_list', kwargs={'slug': SLUG})
POSTS_PROFILE = reverse('posts:profile', kwargs={'username': USERNAME})