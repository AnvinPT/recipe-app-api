from core.models import Tag, Recipe
from decimal import Decimal
from rest_framework import status
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')

def detail_url(tag_id):
    return reverse('recipe:tag-detail', args=[tag_id])

def create_user(email='user@example.com',password='testpass234'):
    return get_user_model().objects.create_user(email,password)


class PublicTagAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_user_unauthorized(self):
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)    


class PrivateTagAPITests(TestCase):    
    
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)


    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user,name='Vegan')
        Tag.objects.create(user=self.user,name='Dessert')
        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)
        
    def test_tags_limited_to_users(self):
        user2 = create_user(email='user2@example.com',password='user2pass')
        Tag.objects.create(user=user2,name='Fruity')
        tag = Tag.objects.create(user=self.user,name='Comfort food')
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'],tag.name)
        self.assertEqual(res.data[0]['id'],tag.id)

    def test_tag_update(self):
        tag = Tag.objects.create(user=self.user, name='hjfj')
        payload ={'name':'dfjjsk'}

        url = detail_url(tag.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name,payload['name'])

    def test_delete_tags(self):
        tag = Tag.objects.create(user=self.user, name='lunch')
        url = detail_url(tag.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code,status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(user=self.user).exists())    
    

    def test_filter_tags_asssigned_to_recipes(self):
        tag1 = Tag.objects.create(user=self.user, name='Dinner')
        tag2 = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = Recipe.objects.create(
            title='Dosa',
            time_minutes=40,
            price=Decimal('3.25'),
            user=self.user,
        )
        recipe.tags.add(tag1)
        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        s1 = TagSerializer(tag1)
        s2 =  TagSerializer(tag2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        tag = Tag.objects.create(user=self.user, name='Lunch')
        Tag.objects.create(user=self.user, name='Dinner')
        recipe1 = Recipe.objects.create(
            title='meals',
            time_minutes=45,
            price=Decimal('70'),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title='fjjk',
            time_minutes=30,
            price=Decimal('25'),
            user=self.user,
        )
        recipe1.tags.add(tag)
        recipe2.tags.add(tag)
        res = self.client.get(TAGS_URL, {'assigned_only': 1})      
        self.assertEqual(len(res.data), 1)