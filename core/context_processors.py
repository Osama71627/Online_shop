from .models import SiteSettings, Category, Banner

def site_settings(request):
    settings = SiteSettings.objects.first()
    categories = Category.objects.all()[:8]
    return {
        'site_settings': settings,
        'categories': categories,
    }
