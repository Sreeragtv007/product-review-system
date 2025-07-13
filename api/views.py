from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from .serializers import ReviewSerializer, UserSerializer, ProductSerializer
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product, Review
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken


# Create your views here.


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=201)
        return Response(serializer.errors, status=400)


class CustomLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({
            'token': token.key,
            'username': token.user.username,
            'role': 'admin' if token.user.is_staff else 'regular'
        })


class ProductListCreateAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Product, pk=pk)

    def get(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response({'message': 'Only admins can add products.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        if not request.user.is_staff:
            return Response({'message': 'Only admins can update products.'}, status=status.HTTP_400_BAD_REQUEST)
        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        if not request.user.is_staff:
            return Response({'message': 'Only admins can update products.'}, status=status.HTTP_400_BAD_REQUEST)
        product = self.get_object(pk)
        if not product:
            return Response({"message": " Product Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReviewSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response({'message': 'Only admins can delete products.'}, status=status.HTTP_403_FORBIDDEN)
        product = self.get_object(pk)
        product.delete()
        return Response({"message": "product deleted sucessfully"}, status=status.HTTP_200_OK)


class ReviewCreateAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        if request.user.is_staff:
            return Response({'message': 'Admins cannot submit reviews.'}, status=status.HTTP_403_FORBIDDEN)

        product_id = int(request.data['product'])

        if not product_id:
            return Response({'message': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        if Review.objects.filter(product_id=product_id, user=request.user).exists():
            return Response({'message': 'You already reviewed this product.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, product_id=product_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductReviewListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, product_id):
        reviews = Review.objects.filter(product_id=product_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
