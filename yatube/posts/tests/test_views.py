from django import forms
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

TEST_PAG_3 = 3


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
            group=cls.group
        )
        cls.private_ref = (
            reverse('posts:post_create'),
            reverse('posts:post_edit',
                    kwargs={'post_id': PostPagesTest.post.id}),
        )
        cls.public_ref = (
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': f'{PostPagesTest.group.slug}'}),
            reverse('posts:profile',
                    kwargs={'username': f'{PostPagesTest.author}'}),
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': f'{PostPagesTest.group.slug}'}):
                   ('posts/group_list.html'),
            reverse('posts:profile',
                    kwargs={'username': f'{PostPagesTest.user}'}):
                   ('posts/profile.html'),
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}): (
                'posts/post_detail.html'
            ),
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}): (
                'posts/create_post.html'
            ),
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_public_views_show_correct_context(self):
        """Проверка, что вью функции для общедоступных страниц
           передают корректный контекст"""
        for revers_name in PostPagesTest.public_ref:
            with self.subTest(revers_name=revers_name):
                response = self.guest_client.get(revers_name)
                for post in response.context['page_obj']:
                    self.assertIsInstance(post, Post)

                first_post = response.context['page_obj'][0]
                self.assertEqual(first_post.text, PostPagesTest.post.text)
                self.assertEqual(first_post.group, PostPagesTest.post.group)
                self.assertEqual(first_post.author, PostPagesTest.post.author)

    def test_pfivate_views_show_correct_context(self):
        """Проверка, что вью функции для приватных старниц
        передают правильный контекст"""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for revers_name in PostPagesTest.private_ref:
            with self.subTest(revers_name=revers_name):
                response = self.authorized_client.get(revers_name)
                for field, type in form_fields.items():
                    with self.subTest(field=field):
                        form_field = (response.context.get('form').
                                      fields.get(field))
                        self.assertIsInstance(form_field, type)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post detailt сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:post_detail',
                        kwargs={'post_id': f'{PostPagesTest.post.id}'})))
        self.assertEqual(response.context.get('posts').text,
                         PostPagesTest.post.text)

    def test_post_show_correct(self):
        """Проверка, что созданый пост появляется
           на нужных страницах"""
        name_pages = [
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': PostPagesTest.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': PostPagesTest.author.username})
        ]

        for page in name_pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertIn(PostPagesTest.post, response.context['page_obj'])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы'
        )

        for i in range(settings.NUM_OF_POSTS_TEST):
            Post.objects.create(
                text='Тестовый текст поста',
                author=cls.author,
                group=cls.group
            )

        cls.paginator_page = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={
                'slug': PaginatorViewsTest.group.slug}),
            reverse('posts:profile', kwargs={
                'username': PaginatorViewsTest.author.username})
        )

    def test_pagenator_at_the_views(self):
        """Тестирование паджинатора"""
        for revers_name in PaginatorViewsTest.paginator_page:
            with self.subTest(revers_name=revers_name):
                response = self.authorized_client.get(revers_name)
                self.assertEqual(len(response.context['page_obj']),
                                 settings.NUM_OF_POSTS_TEST - 3)
                response = self.authorized_client.get(revers_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), TEST_PAG_3)
