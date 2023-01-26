from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
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
        # Неавторизованый пользователь
        self.guest_client = Client()
        # Авторизованый но не автор
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Авторизованый автор
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_index_url_at_desired_location(self):
        """Проверка доступности адреса / для любого пользовтеля."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_index_url_usses_correct_template(self):
        """Проверка шаблона для адреса / для любого пользовтеля."""
        response = self.guest_client.get('/')
        self.assertTemplateUsed(response, 'posts/index.html')

    def test_group_url_at_desired_location(self):
        """Проверяем что страница /group/test-slug/
        доступна любому пользователю"""
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_group_url_usses_correct_template(self):
        """Проверка шаблона для адреса /group/test-slug/
        для любого пользовтеля."""
        response = self.guest_client.get('/group/test-slug/')
        self.assertTemplateUsed(response, 'posts/group_list.html')

    def test_profile_url_at_desired_location(self):
        """Проверка доступности адреса /profile/username/
        для любого пользовтеля."""
        response = self.guest_client.get(f'/profile/{PostURLTests.user}/')
        self.assertEqual(response.status_code, 200)

    def test_profile_url_usses_correct_template(self):
        """Проверка шаблона для адреса /profile/username/
        для любого пользовтеля."""
        response = self.guest_client.get(f'/profile/{PostURLTests.user}/')
        self.assertTemplateUsed(response, 'posts/profile.html')

    def test_url_post_id_at_desired_location(self):
        """Проверка доступности адреса /posts/post_id/
        для любого пользовтеля."""
        response = self.guest_client.get(f'/posts/{PostURLTests.post.id}/')
        self.assertEqual(response.status_code, 200)

    def test_profile_url_usses_correct_template(self):
        """Проверка шаблона для адреса /posts/post_id/
        для любого пользовтеля."""
        response = self.guest_client.get(f'/posts/{PostURLTests.post.id}/')
        self.assertTemplateUsed(response, 'posts/post_detail.html')

    def test_url_edit_post_for_author_at_desired_location(self):
        """Проверка доступности адреса /posts/post_id/edit/
        для автора."""
        response = self.authorized_author.get(f'/posts/{PostURLTests.post.id}'
                                              '/edit/')
        self.assertEqual(response.status_code, 200)

    def test_url_edit_post_for_author_usses_correct_template(self):
        """Проверка шаблона для адреса /posts/post_id/edit/
        для автора."""
        response = self.authorized_author.get(f'/posts/{PostURLTests.post.id}'
                                              '/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_url_create_at_desired_location(self):
        """Проверка доступности адреса /create/
        для авторизовоного пользователя """
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_create_url_usses_correct_templates(self):
        """Проверка шаблона для адреса /create/
        для авторизовоного пользователя"""
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_404_page_is_working(self):
        """Проверка запроса к несуществующей страницы"""
        response = self.guest_client.get('/page_not_found/')
        self.assertEqual(response.status_code, 404)
