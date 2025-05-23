from django.contrib import admin
from django.urls import path, include  # <- Make sure `include` is imported
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),  
    path('', include('ci_cd.urls')),  # <- This should include `ci_cd.urls`
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
