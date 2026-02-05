from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import CustomUser


class RegisterSerializer(serializers.Serializer):
    """Validates the sign-up form: full_name, email, password, confirm_password."""

    full_name = serializers.CharField(max_length=150, trim_whitespace=True)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    # ── field-level ──────────────────────────────────────────────────
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    # ── object-level ─────────────────────────────────────────────────
    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        return CustomUser.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            full_name=validated_data["full_name"],
        )


class LoginSerializer(serializers.Serializer):
    """Validates the login form: email + password."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(email=attrs["email"], password=attrs["password"])
        if user is None:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled.")
        attrs["users"] = user
        return attrs


class UserDetailSerializer(serializers.ModelSerializer):
    """Read-only representation returned after login / on /me."""

    initials = serializers.CharField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ("id", "email", "full_name", "initials", "date_joined")
        read_only_fields = fields
