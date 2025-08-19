from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import CommonUser as User, Account, Country
from finance.models import AcademicYear

class FinanceAPITests(APITestCase):
    def setUp(self):
        # Create a country
        self.country = Country.objects.create(name="Testland", country="TL")
        # Create a user
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        # Create an account and associate it with the user
        self.account = Account.objects.create(
            name="Test School",
            user=self.user,
            school_type="PRIMARY",
            address="123 Test St",
            city="Testville",
            state="Testate",
            zipcode="12345",
            domain_url="test.school.com",
            country=self.country,
        )
        self.client.force_authenticate(user=self.user)

    def test_academic_year_list_view(self):
        """
        Ensure we can list academic years.
        """
        AcademicYear.objects.create(name="2024", school=self.account)
        url = reverse('finance:academicyear-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], '2024')

    def test_finance_category_list_view(self):
        """
        Ensure we can list finance categories.
        """
        url = reverse('finance:financecategory-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
