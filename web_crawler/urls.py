"""web_crawler URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from crawler import views
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('luzzibag/', views.luzzi_web_crawling),
    # path('pau/', views.pau_web_crawling),
    # path('jade/', views.jade_web_crawling),
    path('bana/', views.bana_web_crawling),
    # path('beginning/', views.beginning_web_crawling),
    # path('bnburde/', views.bnburde_web_crawling),
    # path('coming/', views.coming_web_crawling)
]
