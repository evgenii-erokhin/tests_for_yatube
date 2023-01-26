from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user')
        cls.author = User.objects.create(username='author')
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

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        print(PostPagesTest.post)
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}): (
                'posts/group_list.html'
            ),
            reverse('posts:profile', kwargs={'username': 'user'}): (
                'posts/profile.html'
            ),
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


class PagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='user')
        cls.author = User.objects.create(username='author')
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

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_index_page_show_correcr_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_author_0, 'author')
        self.assertEqual(post_group_0, 'Тестовая группа')

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                        kwargs={'slug': 'test-slug'})))
        self.assertEqual(response.context.get('group').title,
                         'Тестовая группа')
        self.assertEqual(response.context.get('group').description,
                         'Тестовое описание группы')
        self.assertEqual(response.context.get('group').slug, 'test-slug')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:profile',
                        kwargs={'username': PagesTest.author.username})))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_author_0, 'author')
        self.assertEqual(post_group_0, 'Тестовая группа')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post detailt сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:post_detail',
                        kwargs={'post_id': f'{PagesTest.post.id}'})))
        self.assertEqual(response.context.get('posts').text,
                         'Тестовый текст')

    def test_create_post_page_show_correct_context(self):
        """Шаблон create post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)

                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон create post для редактирования поста
           сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{PagesTest.post.id}'})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)

                self.assertIsInstance(form_field, expected)

    def test_post_show_correct(self):
        """Проверка, что созданый пост появляется
           на нужных страницах"""
        name_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': PagesTest.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': PagesTest.author.username})
        ]

        for page in name_pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertIn(PagesTest.post, response.context['page_obj'])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='author')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы'
        )

        for i in range(1, settings.NUM_OF_POSTS_TEST):
            cls.posts = Post.objects.create(
                text='Тестовый текст поста',
                author=cls.author,
                group=cls.group
            )

    def test_first_page_of_index_contains_ten_records(self):
        """Тестирование  паджинатора в шаблоне index
           первые десять постов"""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']),
                         settings.TEST_PAG_10)

    def test_second_page_of_index_contains_three_records(self):
        """Тестирование  паджинатора в шаблоне index
           остальные три поста"""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']),
                         settings.TEST_PAG_3)

    def test_first_page_group_list_contains_ten_records(self):
        """Тестирование  паджинатора в шаблоне  group_list
           первые десять постов"""
        response = self.client.get(
            reverse('posts:group_list', kwargs={
                'slug': PaginatorViewsTest.group.slug})
        )
        self.assertEqual(len(response.context['page_obj']),
                         settings.TEST_PAG_10)

    def test_second_page_group_list_contains_three_records(self):
        """Тестирование  паджинатора в шаблоне  group_list
           остальные три поста"""
        response = self.client.get(
            reverse('posts:group_list', kwargs={
                'slug': PaginatorViewsTest.group.slug}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']),
                         settings.TEST_PAG_3)

    def test_first_page_profile_contains_ten_records(self):
        """Тестирование  паджинатора в шаблоне  profile
           первые десять постов"""
        response = self.client.get(
            reverse('posts:profile', kwargs={
                'username': PaginatorViewsTest.author.username})
        )
        self.assertEqual(len(response.context['page_obj']),
                         settings.TEST_PAG_10)

    def test_second_page_profile_contains_three_records(self):
        """Тестирование  паджинатора в шаблоне  profile
           остальные три поста"""
        response = self.client.get(
            reverse('posts:profile', kwargs={
                'username': PaginatorViewsTest.author.username}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']),
                         settings.TEST_PAG_3)
