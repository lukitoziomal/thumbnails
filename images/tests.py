from rest_framework.test import APITestCase
from django.urls import reverse, resolve
from django.core.files.uploadedfile import SimpleUploadedFile
import json

from .models import User, PlanHeight, Plan, Image, Thumbnail, TemporaryLink
from .views import UserImagesView
from .serializers import ImageSerializer


class ImagesAPIViewTest(APITestCase):

    def setUp(self):
        self.plan_height1 = PlanHeight.objects.create(height=200)
        self.plan_height2 = PlanHeight.objects.create(height=400)

        self.plan1 = Plan.objects.create(
            name='Basic',
            original_link=False,
            generate_links=False
        )
        self.plan1.heights.add(self.plan_height1)

        self.plan2 = Plan.objects.create(
            name='Premium',
            original_link=True,
            generate_links=False
        )
        self.plan2.heights.add(self.plan_height1, self.plan_height2)

        self.plan3 = Plan.objects.create(
            name='Enterprise',
            original_link=True,
            generate_links=True
        )
        self.plan3.heights.add(self.plan_height1, self.plan_height2)

        self.username = 'account1'
        self.password = 'xvwa53safgSW'
        self.user = User.objects.create_user(self.username, 'mail@gmail.com', self.password)
        self.user.account_tier = self.plan1

        self.url = reverse('images:user-images-list')

    def test_user_access(self):
        response = self.client.get(self.url)
        # user not logged in
        self.assertEqual(response.status_code, 403)

        # user logged
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.url)
        self.assertTrue(self.client.login(username=self.username, password=self.password))
        self.assertEqual(response.status_code, 200)

        all_url = reverse('images:all-images-list')
        response = self.client.get(all_url)
        self.assertEqual(response.status_code, 403)

    def test_admin_access(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.username, password=self.password)
        url = reverse('images:all-images-list')
        response = self.client.get(url)
        print(response.data)
        self.assertEqual(response.status_code, 200)


