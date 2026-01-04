from django.conf import settings

def env_name(request):
    return {"env": getattr(settings, "ENV_NAME", "dev").lower()}
