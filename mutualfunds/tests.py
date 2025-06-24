from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import FundHouse, Scheme, Portfolio

User = get_user_model()


class MutualFundAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='testpass123')
        self.token = RefreshToken.for_user(self.user).access_token
        self.auth_header = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}

    def test_register_user(self):
        url = reverse('register')
        data = {
            "email": "newuser@example.com",
            "password": "newpass123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "User registered successfully")

    def test_login_user(self):
        url = reverse('token_obtain_pair')
        data = {
            "email": "testuser@example.com",
            "password": "testpass123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data.get('data', {}))

    def test_fetch_fundhouses(self):
        FundHouse.objects.create(name="Axis Mutual Fund")
        url = reverse('fetch-fundhouses')
        response = self.client.get(url, **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Fund houses fetched")

    def test_scheme_list_view(self):
        fund_house = FundHouse.objects.create(name="SBI Mutual Fund")
        scheme = Scheme.objects.create(
            scheme_code=123001,
            scheme_name="SBI Bluechip",
            fund_house=fund_house,
            scheme_type="Open Ended",
            scheme_category="Equity",
            isin_growth="INF200K01968",
            isin_reinvestment="INF200K01AB1",
            is_open_ended=True
        )
        url = reverse('scheme-list', kwargs={"fund_house_id": fund_house.id})
        response = self.client.get(url, **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['data']), 1)

    def test_create_portfolio(self):
        fund_house = FundHouse.objects.create(name="HDFC Mutual Fund")
        scheme = Scheme.objects.create(
            scheme_code=456002,
            scheme_name="HDFC Equity Fund",
            fund_house=fund_house,
            scheme_type="Open Ended",
            scheme_category="Equity",
            isin_growth="INF179K01BY1",
            isin_reinvestment="INF179K01BY2",
            is_open_ended=True
        )
        url = reverse('portfolio')
        data = {
            "scheme": scheme.id,
            "units": 10.5
        }
        response = self.client.post(url, data, **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "Added to portfolio")

    def test_get_portfolio_list(self):
        fund_house = FundHouse.objects.create(name="ICICI MF")
        scheme = Scheme.objects.create(
            scheme_code=789003,
            scheme_name="ICICI Prudential",
            fund_house=fund_house,
            scheme_type="Open Ended",
            scheme_category="Debt",
            isin_growth="INF109K01BW4",
            isin_reinvestment="INF109K01BW5",
            is_open_ended=True
        )
        Portfolio.objects.create(user=self.user, scheme=scheme, units=15.0)
        url = reverse('portfolio')
        response = self.client.get(url, **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Portfolio fetched")
