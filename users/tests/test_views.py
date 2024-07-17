from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from recipe.models import Recipe, RecipeCategory
from users.models import Profile

User = get_user_model()

class UserRegistrationAPITest(APITestCase):
    def setUp(self):
        self.url = reverse('users:create-user')
        self.valid_payload = {
            'email': 'test@example.com',
            'password': 'securepassword',
            'username': 'pradyneel',
        }

    def tearDown(self):
        user = User.objects.filter(email='test@example.com').first()
        if user:
            user.delete()

    def test_register_user(self):
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_invalid_payload(self):
        invalid_payload = {
            'email': 'invalidemail',
            'password': 'short',
        }
        response = self.client.post(self.url, invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLogoutAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='hellouser', password='securepassword', email='testuser123@example.com')
        self.login_url = reverse('users:login-user')

        # Log in the user to get the tokens
        response = self.client.post(self.login_url, {'email': 'testuser123@example.com', 'password': 'securepassword'}, format='json')
        self.access_token = response.data['tokens']['access']
        self.refresh_token = response.data['tokens']['refresh']

        self.url = reverse('users:logout-user')

    def tearDown(self):
        self.user.delete()

    def test_logout(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(self.url, {'refresh': str(self.refresh_token)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_logout_without_token(self):
        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserBookmarkAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='hellouser123', password='securepassword', email='testuser124@example.com')

        # Check if profile already exists for the user
        if not hasattr(self.user, 'profile'):
            self.profile = Profile.objects.create(user=self.user)
        else:
            self.profile = self.user.profile

        self.category = RecipeCategory.objects.create(name='Test Category')
        self.recipe = Recipe.objects.create(
            title='Test Recipe',
            category=self.category,
            desc='Short description',
            cook_time='00:30:00',
            ingredients='Example ingredients',
            procedure='Example procedure',
            author=self.user,
        )
        self.url = reverse('users:user-bookmark', kwargs={'pk': self.user.pk})

    def tearDown(self):
        self.recipe.delete()
        self.category.delete()
        self.profile.delete()
        self.user.delete()

    def test_add_bookmark(self):
        self.client.force_login(self.user)
        payload = {'id': self.recipe.id}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.profile.bookmarks.filter(id=self.recipe.id).exists())

    def test_remove_bookmark(self):
        self.profile.bookmarks.add(self.recipe)
        self.client.force_login(self.user)
        payload = {'id': self.recipe.id}
        response = self.client.delete(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.profile.bookmarks.filter(id=self.recipe.id).exists())

class UserLoginAPITest(APITestCase):
    def setUp(self):
        self.url = reverse('users:login-user')
        self.user = User.objects.create_user(username='testuser', password='securepassword', email='testuser@example.com')

    def tearDown(self):
        self.user.delete()

    def test_login_with_valid_credentials(self):
        payload = {'email': 'testuser@example.com', 'password': 'securepassword'}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_login_with_invalid_credentials(self):
        invalid_payload = {'email': 'testuser@example.com', 'password': 'wrongpassword'}
        response = self.client.post(self.url, invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserProfileAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='securepassword', email='testuser@example.com')
        self.url = reverse('users:user-profile')

    def tearDown(self):
        self.user.delete()

    def test_update_profile(self):
        self.client.force_login(self.user)
        updated_bio = 'Updated bio'
        data = {'bio': updated_bio}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile =Profile.objects.get(user=self.user)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, updated_bio)


    def test_unauthorized_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class PasswordChangeAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='securepassword', email='testuser@example.com')
        self.url = reverse('users:change-password')

    def tearDown(self):
        self.user.delete()

    def test_change_password(self):
        new_password = 'newsecurepassword'
        self.client.force_login(self.user)
        payload = {'old_password': 'securepassword', 'new_password': new_password}
        response = self.client.patch(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the new password works
        login_url = reverse('users:login-user')
        login_payload = {'email': 'testuser@example.com', 'password': new_password}
        login_response = self.client.post(login_url, login_payload, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

    def test_invalid_password_change(self):
        invalid_payload = {'old_password': 'wrongpassword', 'new_password': 'newsecurepassword'}
        self.client.force_login(self.user)
        response = self.client.patch(self.url, invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
