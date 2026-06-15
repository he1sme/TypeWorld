from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from django.shortcuts import redirect

User = get_user_model()


class TypeWorldSocialAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        if sociallogin.is_existing:
            return

        email = (getattr(sociallogin.user, 'email', '') or '').strip()
        if not email:
            email = (sociallogin.account.extra_data.get('email', '') or '').strip()
        if not email:
            return

        user = User.objects.filter(email__iexact=email).first()
        if user:
            sociallogin.connect(request, user)

    def get_connect_redirect_url(self, request, socialaccount):
        return '/profile/'

    def get_login_redirect_url(self, request):
        return '/profile/'
