from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import FundHouse, Scheme, Portfolio
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed


User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed("Invalid email or password")

        if not user.check_password(password):
            raise AuthenticationFailed("Invalid email or password")

        attrs['username'] = user.username  # Important: required by parent serializer
        return super().validate(attrs)

class FundHouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundHouse
        fields = '__all__'

class SchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scheme
        fields = '__all__'

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ['id', 'scheme', 'units', 'current_nav', 'current_value', 'last_updated']
        read_only_fields = ['id', 'current_nav', 'current_value', 'last_updated']

