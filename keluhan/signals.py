import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Laporan

TELEGRAM_TOKEN = "8271645073:AAEQpNuAF9i-kvfP7dAsNSB4f47CvV6VxMAU"
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


@receiver(post_save, sender=Laporan)
def kirim_notifikasi_status(sender, instance, created, **kwargs):

    # Hanya kirim notif jika bukan data baru
    if created:
        return

    pesan = (
        f"📢 Update Status Keluhan\n\n"
        f"Nama: {instance.nama_pengirim}\n"
        f"Status Sekarang: {instance.status}\n"
    )

    try:
        requests.post(
            TELEGRAM_URL,
            data={
                "chat_id": instance.chat_id,
                "text": pesan,
            },
        )
    except Exception as e:
        print("Gagal kirim notifikasi:", e)