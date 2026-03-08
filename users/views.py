from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()

def success_response(message, data=None, status_code=status.HTTP_200_OK):
    response = {'success': True, 'message': message}
    if data:
        response['data'] = data
    return Response(response, status=status_code)

def error_response(message, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({'success': False, 'error': message}, status=status_code)


class RegisterView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        username = request.data.get('username')

        if not email:
            return error_response('Email is required')
        if not password:
            return error_response('Password is required')
        if not username:
            return error_response('Username is required')
        if len(password) < 8:
            return error_response('Password must be at least 8 characters')

        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return success_response('Account created successfully', {
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status.HTTP_201_CREATED)
        return error_response(serializer.errors)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email:
            return error_response('Email is required')
        if not password:
            return error_response('Password is required')

        user = authenticate(request, username=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return success_response('Login successful', {
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
        return error_response('Invalid email or password', status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return error_response('Refresh token is required')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return success_response('Logged out successfully')
        except Exception:
            return error_response('Invalid token')


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return success_response('Profile retrieved', {
            'user': UserSerializer(request.user).data
        })

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response('Profile updated successfully', {
                'user': serializer.data
            })
        return error_response(serializer.errors)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password:
            return error_response('Old password is required')
        if not new_password:
            return error_response('New password is required')
        if len(new_password) < 8:
            return error_response('New password must be at least 8 characters')

        if not request.user.check_password(old_password):
            return error_response('Old password is incorrect')

        request.user.set_password(new_password)
        request.user.save()
        return success_response('Password changed successfully')


class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return error_response('Email is required')

        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            reset_link = f"{frontend_url}/reset-password/{uid}/{token}/"
            send_mail(
                'Reset Your Password - CareerCompass',
                f'Click the link to reset your password: {reset_link}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return success_response('Password reset email sent')
        except User.DoesNotExist:
            return error_response('Email not found', status.HTTP_404_NOT_FOUND)


class ResetPasswordView(APIView):
    def post(self, request, uid, token):
        new_password = request.data.get('new_password')

        if not new_password:
            return error_response('New password is required')
        if len(new_password) < 8:
            return error_response('Password must be at least 8 characters')

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return success_response('Password reset successful')
            return error_response('Invalid or expired token')
        except User.DoesNotExist:
            return error_response('Invalid request')


class GoogleCallbackView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            refresh = RefreshToken.for_user(request.user)
            return success_response('Google login successful', {
                'user': UserSerializer(request.user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
        return error_response('Authentication failed', status.HTTP_401_UNAUTHORIZED)