from django.test import TestCase
from django.urls import reverse


class PublicPagesTests(TestCase):
    def test_static_public_pages_are_accessible(self):
        for name in [
            'core:home',
            'core:about',
            'core:faq',
            'core:contact',
            'core:terms',
            'core:privacy',
        ]:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_discovery_listings_are_public(self):
        self.assertEqual(self.client.get(reverse('subjects:list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('teachers:public_list')).status_code, 200)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('core:dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_booking_create_requires_login(self):
        response = self.client.get(reverse('bookings:create', args=[1]))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
