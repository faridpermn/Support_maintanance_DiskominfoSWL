from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponseRedirect
from django.urls import path
from .models import Laporan, Bidang, AdminBidang
import json


# =====================================================
# CUSTOM ADMIN SITE
# =====================================================
class MyAdminSite(admin.AdminSite):
    site_header = "Kominfo Complaint and Feedback"
    site_title = "Kominfo Admin"
    index_title = "Dashboard Kominfo"

    def has_permission(self, request):
        return request.user.is_active

    # ==========================
    # CUSTOM URL
    # ==========================
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('clear-recent/', self.admin_view(self.clear_recent)),
            path('restore-recent/', self.admin_view(self.restore_recent)),
        ]
        return custom_urls + urls

    # ==========================
    # CLEAR RECENT
    # ==========================
    def clear_recent(self, request):
        now = timezone.now()
        queryset = Laporan.objects.filter(show_in_recent=True)

        if not request.user.is_superuser:
            try:
                admin_bidang = request.user.adminbidang
                queryset = queryset.filter(
                    bidang=admin_bidang.bidang,
                    is_dispatched=True
                )
            except:
                queryset = queryset.none()

        queryset.update(show_in_recent=False, hidden_at=now)
        return HttpResponseRedirect("../")

    # ==========================
    # RESTORE RECENT
    # ==========================
    def restore_recent(self, request):
        batas_restore = timezone.now() - timedelta(days=7)

        queryset = Laporan.objects.filter(
            show_in_recent=False,
            hidden_at__gte=batas_restore
        )

        if not request.user.is_superuser:
            try:
                admin_bidang = request.user.adminbidang
                queryset = queryset.filter(
                    bidang=admin_bidang.bidang,
                    is_dispatched=True
                )
            except:
                queryset = queryset.none()

        queryset.update(show_in_recent=True, hidden_at=None)
        return HttpResponseRedirect("../")

    # ==========================
    # DASHBOARD
    # ==========================
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}

        today = timezone.now()
        seven_days_ago = today - timedelta(days=7)

        laporan_qs = Laporan.objects.all()

        if not request.user.is_superuser:
            try:
                admin_bidang = request.user.adminbidang
                laporan_qs = laporan_qs.filter(
                    bidang=admin_bidang.bidang,
                    is_dispatched=True
                )
            except:
                laporan_qs = laporan_qs.none()

        batas_hapus = timezone.now() - timedelta(days=7)

        laporan_qs.filter(
            show_in_recent=False,
            hidden_at__lte=batas_hapus
        ).delete()

        daily_data = (
            laporan_qs
            .filter(tanggal__gte=seven_days_ago)
            .annotate(day=TruncDay('tanggal'))
            .values('day', 'jenis')
            .annotate(total=Count('id'))
            .order_by('day')
        )

        day_labels = []
        keluhan_day = []
        feedback_day = []

        for data in daily_data:

            if not data['day']:
                continue

            label = data['day'].strftime("%d %b")

            if label not in day_labels:
                day_labels.append(label)
                keluhan_day.append(0)
                feedback_day.append(0)

            index = day_labels.index(label)

            if data['jenis'] == "Keluhan":
                keluhan_day[index] = data['total']

            elif data['jenis'] == "Feedback":
                feedback_day[index] = data['total']

        selesai_data = (
            laporan_qs
            .filter(
                status="Selesai",
                selesai_at__gte=seven_days_ago
            )
            .annotate(day=TruncDay('selesai_at'))
            .values('day')
            .annotate(total=Count('id'))
            .order_by('day')
        )

        selesai_labels = []
        selesai_total = []

        for data in selesai_data:

            if not data['day']:
                continue

            selesai_labels.append(data['day'].strftime("%d %b"))
            selesai_total.append(data['total'])

        recent_laporan = laporan_qs.filter(
            show_in_recent=True
        ).order_by('-tanggal')[:10]

        extra_context.update({
            "day_labels": json.dumps(day_labels),
            "keluhan_day": json.dumps(keluhan_day),
            "feedback_day": json.dumps(feedback_day),
            "selesai_labels": json.dumps(selesai_labels),
            "selesai_total": json.dumps(selesai_total),
            "recent_laporan": recent_laporan,
        })

        return super().index(request, extra_context)


# =====================================================
# FILTER RECYCLE BIN
# =====================================================
class RecycleBinFilter(admin.SimpleListFilter):

    title = "Recycle Bin"
    parameter_name = "deleted"

    def lookups(self, request, model_admin):
        return (("yes", "Tampilkan Terhapus"),)

    def queryset(self, request, queryset):

        if self.value() == "yes":
            return queryset.filter(show_in_recent=False)

        return queryset.filter(show_in_recent=True)


# =====================================================
# LAPORAN ADMIN
# =====================================================
class LaporanAdmin(admin.ModelAdmin):

    list_display = (
        'nama_pengirim',
        'chat_id',
        'bidang',
        'jenis',
        'status',
        'tanggal',
        'status_pengiriman'
    )

    list_filter = ('jenis', 'status', 'bidang', RecycleBinFilter)

    search_fields = (
        'chat_id',
        'nama_pengirim',
        'isi'
    )

    ordering = ('-tanggal',)

    actions = [
        "soft_delete_selected",
        "restore_selected",
        "kirim_ke_bidang"
    ]

    # ==========================
    # STATUS PENGIRIMAN
    # ==========================
    def status_pengiriman(self, obj):

        if obj.is_dispatched:
            return "✅ Terkirim"

        return "❌ Belum dikirim"

    status_pengiriman.short_description = "Dispatch"

    # ==========================
    # FILTER DATA BERDASARKAN ROLE
    # ==========================
    def get_queryset(self, request):

        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        try:
            admin_bidang = request.user.adminbidang

            return qs.filter(
                bidang=admin_bidang.bidang,
                is_dispatched=True
            )

        except:
            return qs.none()

    # ==========================
    # SOFT DELETE
    # ==========================
    def soft_delete_selected(self, request, queryset):

        queryset.update(
            show_in_recent=False,
            hidden_at=timezone.now()
        )

        self.message_user(
            request,
            "Laporan dipindahkan ke Recycle Bin."
        )

    # ==========================
    # RESTORE
    # ==========================
    def restore_selected(self, request, queryset):

        queryset.update(
            show_in_recent=True,
            hidden_at=None
        )

        self.message_user(
            request,
            "Laporan berhasil dipulihkan."
        )

    # ==========================
    # KIRIM KE ADMIN BIDANG
    # ==========================
    def kirim_ke_bidang(self, request, queryset):

        if not request.user.is_superuser:

            self.message_user(
                request,
                "Hanya admin utama yang bisa mengirim laporan.",
                level="error"
            )

            return

        terkirim = 0

        for laporan in queryset:

            if laporan.bidang and not laporan.is_dispatched:

                laporan.is_dispatched = True
                laporan.dikirim_oleh = request.user
                laporan.dikirim_pada = timezone.now()
                laporan.save()

                terkirim += 1

        self.message_user(
            request,
            f"{terkirim} laporan berhasil dikirim ke bidang."
        )


# =====================================================
# ADMIN BIDANG
# =====================================================
class AdminBidangAdmin(admin.ModelAdmin):

    list_display = ("user", "bidang")

    def has_module_permission(self, request):
        return request.user.is_superuser


# =====================================================
# USER ADMIN
# =====================================================
class CustomUserAdmin(UserAdmin):

    def has_module_permission(self, request):
        return request.user.is_superuser


# =====================================================
# REGISTER
# =====================================================
admin_site = MyAdminSite(name='myadmin')

admin_site.register(Laporan, LaporanAdmin)
admin_site.register(Bidang)
admin_site.register(AdminBidang, AdminBidangAdmin)
admin_site.register(User, CustomUserAdmin)