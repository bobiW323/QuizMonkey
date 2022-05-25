"""webapps URL Configuration

The `urlpatterns` list routes URLs to other_views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function other_views
    1. Add an import:  from my_app import other_views
    2. Add a URL to urlpatterns:  path('', other_views.home, name='home')
Class-based other_views
    1. Add an import:  from other_app.other_views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('quizmonkey.urls')),
]
