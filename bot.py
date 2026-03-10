import os
import django
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from asgiref.sync import sync_to_async

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kominfo_webproject.settings")
django.setup()

from keluhan.models import Laporan, Bidang

TOKEN = "8271645073:AAEQpNuAF9i-kvfP7dAsNSB4f47CvV6VxMA"

BIDANG_COMMANDS = {
    "sekretaris": "Sekretaris",
    "administrasi_umum": "Administrasi Umum dan Kepegawaian",
    "administrasi_keuangan": "Administrasi Keuangan dan Pelaporan",
    "layanan_egov": "Bidang Layanan E-Government",
    "informasi_komunikasi": "Bidang Pengelolaan Informasi Komunikasi Publik dan Statistik",
}


# ================= DATABASE =================

@sync_to_async
def get_bidang_by_nama(nama):
    return Bidang.objects.filter(nama__iexact=nama).first()

@sync_to_async
def create_laporan(chat_id, nama_pengirim, text, bidang):
    return Laporan.objects.create(
        chat_id=chat_id,
        nama_pengirim=nama_pengirim,
        isi=text,
        jenis="Keluhan",
        bidang=bidang,
        status="Dikirim",
    )


# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["awaiting_name"] = True

    await update.message.reply_text("Selamat datang di Kominfo.\nSilakan ketik nama Anda terlebih dahulu.")


# ================= HANDLE MESSAGE =================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    chat_id = str(update.message.chat_id)

    # ============ SIMPAN NAMA ============
    if context.user_data.get("awaiting_name"):
        context.user_data["nama_pengirim"] = text
        context.user_data["awaiting_name"] = False

        await update.message.reply_text(
            f"Terima kasih {text}.\n\n"
            "/keluhan - Ajukan Keluhan\n"
            "/feedback - Berikan Feedback"
        )
        return

    # ============ MODE ============
    mode = context.user_data.get("mode")

    if mode == "keluhan":

        bidang_id = context.user_data.get("bidang_id")

        if not bidang_id:
            await update.message.reply_text("Silakan pilih bidang terlebih dahulu.")
            return

        bidang = await sync_to_async(Bidang.objects.get)(id=bidang_id)

        nama_pengirim = context.user_data.get("nama_pengirim")

        await create_laporan(chat_id, nama_pengirim, text, bidang)

        await update.message.reply_text("Keluhan berhasil dikirim.")
        context.user_data.clear()
        return

    await update.message.reply_text("Gunakan /keluhan terlebih dahulu.")


# ================= KELUHAN =================

async def keluhan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.user_data.get("nama_pengirim"):
        await update.message.reply_text("Silakan /start terlebih dahulu.")
        return

    context.user_data["mode"] = "keluhan"

    pesan = "Pilih bidang:\n\n"
    for cmd in BIDANG_COMMANDS:
        pesan += f"/{cmd}\n"

    await update.message.reply_text(pesan)


# ================= PILIH BIDANG =================

async def pilih_bidang(update: Update, context: ContextTypes.DEFAULT_TYPE):

    command = update.message.text.replace("/", "").strip()
    nama_bidang = BIDANG_COMMANDS.get(command)

    bidang = await get_bidang_by_nama(nama_bidang)

    if not bidang:
        await update.message.reply_text("Bidang tidak ditemukan.")
        return

    context.user_data["bidang_id"] = bidang.id

    await update.message.reply_text(
        f"Silakan tulis keluhan untuk bidang {bidang.nama}."
    )


# ================= RUN =================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("keluhan", keluhan))

for cmd in BIDANG_COMMANDS:
    app.add_handler(CommandHandler(cmd, pilih_bidang))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot berjalan...")
app.run_polling()