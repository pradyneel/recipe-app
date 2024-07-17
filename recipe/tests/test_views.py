from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from recipe.models import Recipe, RecipeLike, RecipeCategory

User = get_user_model()

class RecipeLikeAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='testuser124@example.com')
        self.recipe = Recipe.objects.create(
            title='Test Recipe',
            author=self.user,
            category=RecipeCategory.objects.create(name='Test Category'),
            picture='test.jpg',
            desc='Test description',
            cook_time='00:30:00',
            ingredients='Test ingredients',
            procedure='Test procedure'
        )
        self.like_url = reverse('recipe:recipe-like', kwargs={'pk': self.recipe.pk})
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        self.user.delete()
        self.recipe.delete()

    def test_like_recipe(self):
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(RecipeLike.objects.filter(user=self.user, recipe=self.recipe).exists())

    def test_unlike_recipe(self):
        like = RecipeLike.objects.create(user=self.user, recipe=self.recipe)
        response = self.client.delete(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(RecipeLike.objects.filter(user=self.user, recipe=self.recipe).exists())

    def test_like_already_liked_recipe(self):
        RecipeLike.objects.create(user=self.user, recipe=self.recipe)
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unlike_not_liked_recipe(self):
        response = self.client.delete(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
