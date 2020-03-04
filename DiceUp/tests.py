from django.test import SimpleTestCase, TestCase, Client
from django.urls import reverse, resolve
from django.core.files.uploadedfile import UploadedFile

from DiceUp.views import HomeView, example
from DiceUp.models import DiceUpModel


class TestUrls(SimpleTestCase):

    def test_HomeView_url(self):
        url = reverse('DiceUp:home')
        self.assertEqual(resolve(url).func.view_class, HomeView)

    def test_example_url(self):
        url = reverse('DiceUp:example')
        self.assertEqual(resolve(url).func, example)


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.home_url = reverse('DiceUp:home')
        self.test_image_dir = 'DiceUp/test_images/'

    def test_HomeView_GET(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'DiceUp/home.html')

    def test_HomeView_POST_valid_image(self):
        image_path = self.test_image_dir + 'valid.jpg'
        uploaded_file = open(image_path, 'rb')
        response = self.client.post(self.home_url, {'original_picture': uploaded_file, 'range': -3})
        self.assertTemplateUsed(response, 'DiceUp/success.html')

    def test_HomeView_POST_invalid_image(self):
        invalid_images_list = ['too_heavy.png', 'too_large.jpg', 'too_small.jpg']
        for image in invalid_images_list:
            uploaded_file = open(self.test_image_dir + image, 'rb')
            response = self.client.post(self.home_url, {'original_picture': uploaded_file, 'range': -3})
            self.assertTemplateUsed(response, 'DiceUp/home.html')

    def test_HomeView_PPOST_invalid_range(self):
        image_path = self.test_image_dir + 'valid.jpg'
        uploaded_file = open(image_path, 'rb')
        print(self.client.post(self.home_url, {'original_picture': uploaded_file, 'range': 0}))