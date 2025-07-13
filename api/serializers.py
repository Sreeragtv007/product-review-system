from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Review


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class ReviewSerializer(serializers.ModelSerializer):
        user = serializers.StringRelatedField(read_only=True)

        class Meta:
            model = Review
            fields = ['id', 'product', 'user', 'rating', 'feedback']
            read_only_fields = ['user']


class ProductSerializer(serializers.ModelSerializer):
    average_ratings = serializers.FloatField(
        source='average_rating', read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description',
                  'price', 'average_ratings', 'reviews']
