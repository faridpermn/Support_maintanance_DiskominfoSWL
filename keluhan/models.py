from django.db import models, transaction
from django.utils import timezone
from django.contrib.auth.models import User
import requests


# ==========================
# MODEL BIDANG
# ==========================
class Bidang(models.Model):

    BIDANG_CHOICES = [
        ("Sekretaris", "Sekretaris"),
        ("Administrasi Umum dan Kepegawaian", "Administrasi Umum dan Kepegawaian"),
        ("Administrasi Keuangan dan Pelaporan", "Administrasi Keuangan dan Pelaporan"),
        ("Bidang Layanan E-Government", "Bidang Layanan E-Government"),
        (
            "Bidang Pengelolaan Informasi Komunikasi Publik dan Statistik",
            "Bidang Pengelolaan Informasi Komunikasi Publik dan Statistik",
        ),
    ]

    nama = models.CharField(max_length=200, choices=BIDANG_CHOICES, unique=True)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name_plural = "Bidang"
        ordering = ["nama"]


# ==========================
# MODEL LAPORAN
# ==========================
class Laporan(models.Model):

    JENIS_CHOICES = [
        ("Keluhan", "Keluhan"),
        ("Feedback", "Feedback"),
    ]

    STATUS_CHOICES = [
        ("Dikirim", "Dikirim"),
        ("Diproses", "Diproses"),
        ("Selesai", "Selesai"),
    ]

    chat_id = models.CharField(max_length=100)
    nama_pengirim = models.CharField(max_length=150, null=True, blank=True)

    isi = models.TextField()
    jenis = models.CharField(max_length=20, choices=JENIS_CHOICES)

    bidang = models.ForeignKey(
        Bidang,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="laporan"
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="Dikirim"
    )

    tanggal = models.DateTimeField(auto_now_add=True)
    selesai_at = models.DateTimeField(null=True, blank=True)

    show_in_recent = models.BooleanField(default=True)
    hidden_at = models.DateTimeField(null=True, blank=True)

    # ==========================
    # DISPATCH SYSTEM (ADMIN UTAMA → ADMIN BIDANG)
    # ==========================
    is_dispatched = models.BooleanField(default=False)

    dikirim_oleh = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="laporan_dikirim"
    )

    dikirim_pada = models.DateTimeField(null=True, blank=True)

    # ==========================
    # SAVE OVERRIDE (TIDAK DIUBAH LOGIKA)
    # ==========================
    def save(self, *args, **kwargs):

        status_lama = None

        if self.pk:
            try:
                status_lama = Laporan.objects.get(pk=self.pk).status
            except Laporan.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        if status_lama and status_lama != self.status:

            if self.status == "Selesai" and not self.selesai_at:
                self.selesai_at = timezone.now()
                super().save(update_fields=["selesai_at"])

            transaction.on_commit(
                lambda: self.kirim_notifikasi_status()
            )

    # ==========================
    # NOTIF TELEGRAM
    # ==========================
    def kirim_notifikasi_status(self):

        TELEGRAM_TOKEN = "8271645073:AAEQpNuAF9i-kvfP7dAsNSB4f47CvV6VxMA"
        TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        pesan = (
            f"📢 Update Status Laporan\n\n"
            f"Nama: {self.nama_pengirim or '-'}\n"
            f"Jenis: {self.jenis}\n"
            f"Status Sekarang: {self.status}\n"
        )

        try:
            requests.post(
                TELEGRAM_URL,
                data={
                    "chat_id": self.chat_id,
                    "text": pesan,
                },
                timeout=5
            )
        except Exception as e:
            print("Gagal kirim notifikasi:", e)

    def __str__(self):
        return f"{self.nama_pengirim or self.chat_id} - {self.jenis} - {self.status}"

    class Meta:
        ordering = ["-tanggal"]


# ==========================
# MODEL ADMIN BIDANG
# ==========================
class AdminBidang(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="adminbidang"
    )

    bidang = models.ForeignKey(
        Bidang,
        on_delete=models.CASCADE,
        related_name="admin_pengampu"
    )

    aktif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.bidang.nama}"

    class Meta:
        verbose_name = "Admin Bidang"
        verbose_name_plural = "Admin Bidang"