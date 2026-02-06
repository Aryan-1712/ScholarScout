from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

User = get_user_model()


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    email = request.data.get("email", "").strip().lower()
    password = request.data.get("password", "")
    full_name = request.data.get("full_name", "").strip()

    if not email:
        return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

    if not password:
        return Response({"error": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)

    if len(password) < 8:
        return Response({"error": "Password must be at least 8 characters long"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({"error": "An account with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        email=email,
        password=password,
        full_name=full_name
    )

    token, _ = Token.objects.get_or_create(user=user)

    return Response(
        {
            "message": "Account created successfully",
            "token": token.key,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
            },
        },
        status=status.HTTP_201_CREATED
    )


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get("email", "").strip().lower()
    password = request.data.get("password", "")

    if not email or not password:
        return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

    # IMPORTANT: use username=email
    user = authenticate(request, username=email, password=password)

    if user is None:
        return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

    token, _ = Token.objects.get_or_create(user=user)

    return Response(
        {
            "message": "Login successful",
            "token": token.key,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
            },
        },
        status=status.HTTP_200_OK
    )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

from django.shortcuts import render

def dashboard(request):
    return render(request, "dashboard.html")
