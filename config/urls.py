from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # NOUVEAU : On active le système d'authentification natif de Django
    path('accounts/', include('django.contrib.auth.urls')), 
    
    path('api/', include('finance.urls')),
]