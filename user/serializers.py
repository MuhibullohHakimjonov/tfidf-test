from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.utils.crypto import get_random_string
from .tasks import send_verification_email_task
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
	email = serializers.EmailField()
	username = serializers.CharField()
	password = serializers.CharField(write_only=True)

	def validate_email(self, value):
		if User.objects.filter(email=value).exists():
			raise serializers.ValidationError("Email is already registered.")
		return value

	def validate_username(self, value):
		if User.objects.filter(username=value).exists():
			raise serializers.ValidationError("Username is already taken.")
		return value

	def create(self, validated_data):
		email = validated_data["email"]
		username = validated_data["username"]
		password = validated_data["password"]
		verification_code = get_random_string(length=6, allowed_chars='0123456789')

		cache.set(
			f"temp_user:{email}",
			{
				"email": email,
				"username": username,
				"password": password,
				"code": verification_code,
			},
			timeout=300
		)
		cache.set(f"resend_block:{email}", True, timeout=60)

		send_verification_email_task.delay(email, verification_code)
		return {"email": email}


class VerifyCodeSerializer(serializers.Serializer):
	email = serializers.EmailField()
	code = serializers.CharField(max_length=6)

	def validate(self, data):
		email = data["email"]
		code = data["code"]
		cached = cache.get(f"temp_user:{email}")

		if not cached:
			raise serializers.ValidationError("No registration data found or code expired.")

		if cached["code"] != code:
			raise serializers.ValidationError("Invalid verification code.")

		return data

	def save(self):
		email = self.validated_data["email"]
		cached = cache.get(f"temp_user:{email}")
		if not cached:
			raise serializers.ValidationError("Registration data expired.")
		user = User.objects.create_user(
			email=cached["email"],
			username=cached["username"],
			password=cached["password"],
			is_active=True
		)
		cache.delete(f"temp_user:{email}")
		cache.delete(f"resend_block:{email}")
		return user


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ['id', 'email', 'username']


class UserUpdateSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ['email', 'username']
		read_only_fields = ['email']


class ChangePasswordSerializer(serializers.ModelSerializer):
	old_password = serializers.CharField(write_only=True)
	new_password = serializers.CharField(write_only=True)

	class Meta:
		model = User
		fields = ['old_password', 'new_password']

	def validate_old_password(self, value):
		user = self.context['request'].user
		if not user.check_password(value):
			raise ValidationError("Old password is incorrect")
		return value

	def validate_new_password(self, value):
		validate_password(value)
		return value
