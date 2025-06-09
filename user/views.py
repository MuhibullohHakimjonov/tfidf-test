import random

from django.contrib.auth import logout
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.core.cache import cache
from rest_framework import status, generics, permissions, viewsets
from rest_framework.response import Response
from .serializers import RegisterSerializer, ChangePasswordSerializer, UserSerializer, UserUpdateSerializer, \
	VerifyCodeSerializer
from .tasks import send_verification_email_task


class RegisterView(generics.GenericAPIView):
	serializer_class = RegisterSerializer

	def post(self, request):
		email = request.data.get("email")
		if cache.get(f"resend_block:{email}"):
			return Response(
				{"error": "Please wait 1 minute before resending the code."},
				status=status.HTTP_429_TOO_MANY_REQUESTS,
			)

		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(
				{"message": "Verification code sent successfully."},
				status=status.HTTP_201_CREATED
			)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailCodeView(generics.GenericAPIView):
	serializer_class = VerifyCodeSerializer

	def post(self, request):
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(
				{"message": "User verified and registered successfully."},
				status=status.HTTP_200_OK
			)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationCodeView(APIView):
	serializer_class = VerifyCodeSerializer

	def post(self, request):
		email = request.data.get('email')

		cached_data = cache.get(f"temp_user:{email}")
		if not cached_data:
			return Response({"error": "User data not found or expired."}, status=400)

		if cache.get(f"resend_block:{email}"):
			return Response({"error": "Wait 1 minute before resending code."}, status=429)

		verification_code = ''.join(random.choices('0123456789', k=6))
		cached_data["code"] = verification_code

		cache.set(f"temp_user:{email}", cached_data, timeout=300)
		cache.set(f"resend_block:{email}", True, timeout=60)

		send_verification_email_task.delay(email, verification_code)

		return Response({"message": "Verification code resent successfully."}, status=status.HTTP_200_OK)


class LogoutView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request):
		logout(request)
		return Response({"message": "Logged out"}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ViewSet):
	permission_classes = [permissions.IsAuthenticated]

	@action(detail=False, methods=['get'], url_path='me')
	@extend_schema(responses=UserSerializer)
	def me(self, request):
		serializer = UserSerializer(request.user)
		return Response(serializer.data)

	@me.mapping.put
	@extend_schema(request=UserUpdateSerializer, responses={"200": {"message": "Profile updated"}})
	def update_me(self, request):
		serializer = UserUpdateSerializer(request.user, data=request.data, partial=True, context={'request': request})
		if serializer.is_valid():
			serializer.save()
			return Response({"message": "Profile updated"})
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@extend_schema(request=None, responses={204: None})
	@me.mapping.delete
	def delete_me(self, request):
		request.user.delete()
		return Response({"message": "Account deleted"}, status=status.HTTP_204_NO_CONTENT)

	@action(detail=False, methods=['put'], url_path='change-password')
	@extend_schema(request=ChangePasswordSerializer)
	def change_password(self, request):
		serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
		if serializer.is_valid():
			request.user.set_password(serializer.validated_data['new_password'])
			request.user.save()
			return Response({"message": "Password changed successfully"})
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
