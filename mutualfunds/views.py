from rest_framework import generics, permissions, status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    FundHouseSerializer,
    SchemeSerializer,
    PortfolioSerializer
)
from .models import FundHouse, Scheme, Portfolio, NAV
from .utils import success_response, error_response
import requests
from decouple import config


HEADERS = {
    "X-RapidAPI-Key": config("RAPIDAPI_KEY"),
    "X-RapidAPI-Host": config("RAPID_API_HOST")
}

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return success_response("User registered successfully", serializer.data, status.HTTP_201_CREATED)
        except Exception as e:
            return error_response("Registration failed", str(e))
            

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            return success_response("Login successful", response.data)
        except Exception as e:
            return error_response("Login failed", str(e), status.HTTP_401_UNAUTHORIZED)



# Fetch and Save Fund Houses
class FetchAndSaveFundHousesView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FundHouseSerializer

    def post(self, request, *args, **kwargs):
        try:
            url = f"https://{config('RAPID_API_HOST')}/latest"

            response = requests.get(url, headers=HEADERS, timeout=60)

            if response.status_code == 200:
                data = response.json()
                fund_houses = set(s.get("Mutual_Fund_Family") for s in data if s.get("Mutual_Fund_Family"))

                created = 0
                for name in fund_houses:
                    _, is_created = FundHouse.objects.get_or_create(name=name)
                    if is_created:
                        created += 1

                return success_response(f"{created} fund houses added.", {"created": created})
            return error_response("Failed to fetch fund houses", response.text, status.HTTP_502_BAD_GATEWAY)

        except Exception as e:
            return error_response("Error occurred", str(e))
    
    def get(self, request, *args, **kwargs):
        try:
            fundhouses = FundHouse.objects.all()
            serializer = self.get_serializer(fundhouses, many=True)
            return success_response("Fund houses fetched", serializer.data)
        except Exception as e:
            return error_response("Error fetching fund houses", str(e))


# Fetch and Save Open-Ended Schemes
class FetchAndSaveSchemesView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SchemeSerializer

    def post(self, request, *args, **kwargs):
        try:
            url = f"https://{config('RAPID_API_HOST')}/latest"

            response = requests.get(url, headers=HEADERS, timeout=60)

            if response.status_code == 200:
                data = response.json()
                created = 0
                skipped = 0

                for item in data:
                    if "open" not in item.get("Scheme_Type", "").lower():
                        continue

                    fund_house_name = item.get("Mutual_Fund_Family")
                    if not fund_house_name:
                        continue

                    fund_house, _ = FundHouse.objects.get_or_create(name=fund_house_name)

                    scheme_code = item.get("Scheme_Code")
                    if not scheme_code:
                        skipped += 1
                        continue

                    _, is_created = Scheme.objects.get_or_create(
                        scheme_code=scheme_code,
                        defaults={
                            "scheme_name": item.get("Scheme_Name"),
                            "fund_house": fund_house,
                            "scheme_type": item.get("Scheme_Type"),
                            "scheme_category": item.get("Scheme_Category"),
                            "isin_growth": item.get("ISIN_Div_Payout_ISIN_Growth"),
                            "isin_reinvestment": item.get("ISIN_Div_Reinvestment"),
                            "is_open_ended": True
                        }
                    )
                    if is_created:
                        created += 1

                return success_response(f"{created} schemes added, {skipped} skipped.", {"created": created, "skipped": skipped})
            return error_response("Failed to fetch schemes", response.text, status.HTTP_502_BAD_GATEWAY)

        except Exception as e:
            return error_response("Error occurred", str(e))


# List Open-Ended Schemes for a Fund House
class SchemeListView(generics.ListAPIView):
    serializer_class = SchemeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        fund_house_id = self.kwargs.get('fund_house_id')
        return Scheme.objects.filter(fund_house_id=fund_house_id, is_open_ended=True)


# Create and List Portfolio with latest NAV
class PortfolioListCreateView(generics.ListCreateAPIView):
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user).select_related("scheme")

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            portfolio_data = []

            for item in queryset:
                nav_obj = NAV.objects.filter(scheme=item.scheme).order_by('-date').first()
                current_nav = nav_obj.nav if nav_obj else 0.0
                current_value = round(item.units * current_nav, 2)
                
                portfolio_data.append({
                    "id": item.id,
                    "scheme": SchemeSerializer(item.scheme).data,
                    "units": item.units,
                    "current_value": current_value,
                    "last_updated": item.last_updated
                })

            return success_response("Portfolio fetched", portfolio_data)
        except Exception as e:
            return error_response("Failed to fetch portfolio", str(e))

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save(user=request.user)
            return success_response("Added to portfolio", PortfolioSerializer(instance).data, status.HTTP_201_CREATED)
        except Exception as e:
            return error_response("Failed to add to portfolio", str(e))
