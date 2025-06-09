from django.urls import path, include
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import (
	TokenObtainPairView,
)

from .views import RegisterView, LogoutView, VerifyEmailCodeView, ResendVerificationCodeView, UserViewSet

router = DefaultRouter()
router.register('user', UserViewSet, basename='user')

urlpatterns = [
	# profile
	path('', include(router.urls)),

	# auth
	path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
	path("register/", RegisterView.as_view()),
	path("verify-email/", VerifyEmailCodeView.as_view()),
	path('resend-code/', ResendVerificationCodeView.as_view()),
	path("logout/", LogoutView.as_view()),
]
