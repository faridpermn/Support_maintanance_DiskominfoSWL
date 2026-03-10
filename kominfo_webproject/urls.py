"""
URL configuration for kominfo_webproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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

# Semua view diambil dari app pengaduan (bukan dari .views)
from django.urls import path
from keluhan.admin import admin_site
from . import views

urlpatterns = [
    # ==========================
    # HALAMAN LANDING
    # ==========================
    path('', views.landing, name='landing'),

    # ==========================
    # DASHBOARD
    # ==========================
    path('dashboard/', views.dashboard, name='dashboard'),

    # ==========================
    # ADMIN KOMINFO
    # ==========================
    path('admin/', admin_site.urls),

    # ==========================
    # EXPORT LAPORAN PDF
    # ==========================
    path('laporan-pdf/', views.laporan_keluhan_pdf, name='laporan_pdf'),

    # ==========================
    # HALAMAN TUTORIAL PENGGUNA
    # ==========================
    path('tutorial/', views.tutorial, name='tutorial'),
]