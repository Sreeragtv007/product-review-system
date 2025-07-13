from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from .serializers import ReviewSerializer, UserSerializer, ProductSerializer
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product, Review


# Create your views here.


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "user registration sucess"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return Response({"message": "Login successful", "username": user.username}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


class ProductListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response({'detail': 'Only admins can add products.'}, status=403)
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ProductDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Product, pk=pk)

    def get(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        if not request.user.is_staff:
            return Response({'detail': 'Only admins can update products.'}, status=403)
        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response({'detail': 'Only admins can delete products.'}, status=403)
        product = self.get_object(pk)
        product.delete()
        return Response(status=204)

    class ReviewCreateAPIView(APIView):
        permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.is_staff:
            return Response({'detail': 'Admins cannot submit reviews.'}, status=status.HTTP_403_FORBIDDEN)

        product_id = request.data.get('product')
        if not product_id:
            return Response({'detail': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        if Review.objects.filter(product_id=product_id, user=request.user).exists():
            return Response({'detail': 'You already reviewed this product.'}, status=status.HTTP_400_BAD_REQUEST0)

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, product_id=product_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
