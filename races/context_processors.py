import os

def _has_env_pair(a, b):

    return bool(os.environ.get(a, '').strip() and os.environ.get(b, '').strip())

def typeworld_auth(request):

    google_enabled = _has_env_pair('GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET')

    vk_enabled = _has_env_pair('VK_CLIENT_ID', 'VK_CLIENT_SECRET')

    try:

        from allauth.socialaccount.models import SocialApp

        google_enabled = google_enabled or SocialApp.objects.filter(provider='google').exists()

        vk_enabled = vk_enabled or SocialApp.objects.filter(provider='vk').exists()

    except Exception:

        pass

    crystals = 0

    if getattr(request.user, 'is_authenticated', False):

        try:

            from .models import UserProfile

            profile, _ = UserProfile.objects.get_or_create(user=request.user)

            crystals = profile.crystals

        except Exception:

            crystals = 0

    return {

        'google_oauth_enabled': google_enabled,

        'vk_oauth_enabled': vk_enabled,

        'site_url': os.environ.get('TYPEWORLD_PUBLIC_URL', 'http://127.0.0.1:8000').rstrip('/'),

        'typeworld_crystals': crystals,

    }
