# RANCANG BANGUN SISTEM
# Aplikasi Keluhan dan Feedback Diskominfo Sawahlunto

---

## 1. PENDAHULUAN

### 1.1 Latar Belakang
Sistem Informasi Pengelolaan Keluhan dan Feedback Dinas Komunikasi dan Informatika (Diskominfo) Kota Sawahlunto adalah sebuah aplikasi berbasis web yang terintegrasi dengan Telegram Bot untuk menerima dan mengelola keluhan serta feedback dari masyarakat. Sistem ini bertujuan untuk meningkatkan responsivitas pemerintah daerah dalam menangani keluhan publik secara efisien dan terstruktur.

### 1.2 Tujuan Sistem
- Menyediakan saluran komunikasi yang mudah diakses masyarakat untuk menyampaikan keluhan dan feedback
- Memudahkan petugas Diskominfo dalam mengelola dan menindaklanjuti keluhan
- Menyediakan dashboard analitik untuk memantau kinerja penanganan keluhan
- Mengintegrasikan notifikasi otomatis melalui Telegram

### 1.3 Ruang Lingkup
- Sistem pengelolaan keluhan dan feedback berbasis Web (Django)
- Integrasi Telegram Bot untuk penerimaan keluhan
- Sistem dispatch (penyaluran) laporan ke bidang terkait
- Dashboard admin dengan fitur analitik
- Sistem multi-user dengan role Admin Utama dan Admin Bidang

---

## 2. ARSITEKTUR SISTEM

### 2.1 Arsitektur Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ARSITEKTUR SISTEM                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌──────────────┐         ┌──────────────────┐        ┌────────────┐  │
│   │   MASYARAKAT │         │   TELEGRAM BOT   │        │   ADMIN   │  │
│   │  (User)      │────────▶│   @KomiSwl_bot   │────────│  PANEL    │  │
│   └──────────────┘         └──────────────────┘        └─────┬──────┘  │
│                                                                 │        │
│                                │                                 │        │
│                                ▼                                 ▼        │
│                    ┌─────────────────────────────────────────────┐      │
│                    │              DJANGO APPLICATION              │      │
│                    │  ┌─────────────┐  ┌─────────────────────┐   │      │
│                    │  │   Views     │  │   Admin Interface   │   │      │
│                    │  └─────────────┘  └─────────────────────┘   │      │
│                    │  ┌─────────────┐  ┌─────────────────────┐   │      │
│                    │  │   Models    │  │   Business Logic    │   │      │
│                    │  └─────────────┘  └─────────────────────┘   │      │
│                    └─────────────────────┬───────────────────────┘      │
│                                          │                              │
│                                          ▼                              │
│                    ┌─────────────────────────────────────────────┐      │
│                    │              DATABASE (SQLite)               │      │
│                    └─────────────────────────────────────────────┘      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Arsitektur Layers

```
┌────────────────────────────────────────┐
│        PRESENTATION LAYER              │
│  - Landing Page (HTML/CSS)             │
│  - Admin Dashboard                     │
│  - Tutorial Page                       │
└────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────┐
│        APPLICATION LAYER               │
│  - Django Views                        │
│  - Django Admin                        │
│  - Telegram Bot Handlers              │
│  - Business Logic (Models)            │
└────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────┐
│        DATA LAYER                      │
│  - Django ORM                          │
│  - SQLite Database                     │
│  - Telegram API                        │
└────────────────────────────────────────┘
```

---

## 3. DESAIN DATABASE

### 3.1 Entity Relationship Diagram

```
┌─────────────────────┐       ┌─────────────────────┐
│       USER         │       │      BIDANG         │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)            │       │ id (PK)             │
│ username          │       │ nama                │
│ password          │       │                     │
│ email             │       │                     │
│ is_superuser      │       │                     │
│ is_staff          │       │                     │
└─────────────────────┘       └──────────┬──────────┘
                                         │
                                         │ 1:N
                                         ▼
                              ┌─────────────────────┐
                              │      LAPORAN        │
                              ├─────────────────────┤
                              │ id (PK)             │
                              │ chat_id             │
                              │ nama_pengirim       │
                              │ isi                 │
                              │ jenis               │
          ┌───────────────────│ status              │
          │                   │ tanggal             │
          │                   │ selesai_at          │
          │                   │ show_in_recent      │
          │                   │ hidden_at           │
          │                   │ is_dispatched       │
          │                   │ dikirim_oleh (FK)   │
          │                   │ dikirim_pada        │
          │                   │ bidang_id (FK)      │
          └───────────────────┴──────────┬──────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │    ADMIN BIDANG     │
                              ├─────────────────────┤
                              │ id (PK)             │
                              │ user_id (FK)        │
                              │ bidang_id (FK)      │
                              │ aktif               │
                              │ created_at          │
                              └─────────────────────┘
```

### 3.2 Detail Tabel

#### Tabel: Bidang
| Field | Type | Constraint | Keterangan |
|-------|------|------------|------------|
| id | AutoField | PK | ID Bidang |
| nama | CharField(200) | Unique | Nama Bidang |

**Daftar Bidang:**
1. Sekretaris
2. Administrasi Umum dan Kepegawaian
3. Administrasi Keuangan dan Pelaporan
4. Bidang Layanan E-Government
5. Bidang Pengelolaan Informasi Komunikasi Publik dan Statistik

#### Tabel: Laporan
| Field | Type | Constraint | Keterangan |
|-------|------|------------|------------|
| id | AutoField | PK | ID Laporan |
| chat_id | CharField(100) | - | ID Telegram Chat |
| nama_pengirim | CharField(150) | Null, Blank | Nama Pengirim |
| isi | TextField | - | Isi Keluhan/Feedback |
| jenis | CharField(20) | Choices | "Keluhan" atau "Feedback" |
| bidang_id | ForeignKey | Null, Blank | Relasi ke Bidang |
| status | CharField(50) | Default: "Dikirim" | Status Laporan |
| tanggal | DateTimeField | Auto Now Add | Tanggal Dibuat |
| selesai_at | DateTimeField | Null, Blank | Tanggal Selesai |
| show_in_recent | BooleanField | Default: True | Tampil di Recent |
| hidden_at | DateTimeField | Null, Blank | Tanggal Disembunyikan |
| is_dispatched | BooleanField | Default: False | Sudah Dikirim ke Bidang |
| dikirim_oleh_id | ForeignKey | Null, Blank | User yang Mengirim |
| dikirim_pada | DateTimeField | Null, Blank | Tanggal Pengiriman |

**Status Laporan:**
- Dikirim → Diproses → Selesai

#### Tabel: AdminBidang
| Field | Type | Constraint | Keterangan |
|-------|------|------------|------------|
| id | AutoField | PK | ID Admin Bidang |
| user_id | ForeignKey | - | Relasi ke User Django |
| bidang_id | ForeignKey | - | Relasi ke Bidang |
| aktif | BooleanField | Default: True | Status Aktif |
| created_at | DateTimeField | Auto Now Add | Tanggal Dibuat |

---

## 4. FITUR SISTEM

### 4.1 Fitur Utama

#### A. Telegram Bot (@KomiSwl_bot)
| Fitur | Deskripsi |
|-------|-----------|
| /start | Memulai interaksi, meminta nama user |
| /keluhan | Memulai proses pengajuan keluhan |
| /feedback | Memulai proses pemberian feedback |
| Pemilihan Bidang | User memilih bidang tujuan |
| Notifikasi Status | Mengirim notifikasi saat status berubah |

#### B. Panel Admin
| Fitur | Deskripsi |
|-------|-----------|
| Dashboard | Grafik keluhan/feedback 7 hari terakhir |
| Kelola Laporan | View, Edit, Delete laporan |
| Dispatch System | Menyalurkan laporan ke bidang terkait |
| Recycle Bin | Soft delete dan restore laporan |
| Filter & Search | Mencari laporan berdasarkan kriteria |
| Statistik | Data jumlah keluhan per hari |

#### C. Landing Page
| Fitur | Deskripsi |
|-------|-----------|
| Link Telegram Bot | Akses langsung ke bot |
| Link Login Admin | Akses ke panel admin |
| Tutorial | Panduan penggunaan sistem |

### 4.2 Fitur Berdasarkan Role

#### Admin Utama (Superuser)
- Melihat semua laporan dari seluruh bidang
- Dispatch laporan ke bidang terkait
- Mengelola user admin bidang
- Soft delete dan restore laporan
- Akses ke recycle bin
- Melihat statistik lengkap

#### Admin Bidang
- Melihat hanya laporan dari bidang sendiri (setelah di-dispatch)
- Mengubah status laporan (Diproses → Selesai)
- Soft delete laporan bidang sendiri
- Melihat statistik bidang sendiri

---

## 5. FLOW PENGGUNAAN

### 5.1 Flow Masyarakat Mengajukan Keluhan

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Masyarakat │     │   Telegram  │     │   Database  │     │    Admin    │
│             │     │    Bot      │     │             │     │   Bidang    │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       │  1. /start        │                   │                   │
       │──────────────────▶│                   │                   │
       │                   │                   │                   │
       │  2. Input Nama    │                   │                   │
       │──────────────────▶│                   │                   │
       │                   │                   │                   │
       │  3. /keluhan      │                   │                   │
       │──────────────────▶│                   │                   │
       │                   │                   │                   │
       │  4. Pilih Bidang  │                   │                   │
       │──────────────────▶│                   │                   │
       │                   │                   │                   │
       │  5. Input Keluhan │                   │                   │
       │──────────────────▶│                   │                   │
       │                   │  6. Save Laporan  │                   │
       │                   │──────────────────▶│                   │
       │                   │                   │                   │
       │  7. Konfirmasi    │                   │                   │
       │◀──────────────────│                   │                   │
       │                   │                   │                   │
       │                   │                   │   8. View Laporan │
       │                   │                   │─────────────────▶│
       │                   │                   │                   │
```

### 5.2 Flow Penanganan Keluhan

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Admin     │     │   Sistem    │     │   Database  │     │  Telegram   │
│  Utama     │     │             │     │             │     │    Bot      │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       │  1. View Laporan │                   │                   │
       │──────────────────▶│                   │                   │
       │                   │  2. Get Data     │                   │
       │                   │──────────────────▶│                   │
       │                   │◀──────────────────│                   │
       │                   │                   │                   │
       │  3. Dispatch ke   │                   │                   │
       │     Bidang        │                   │                   │
       │──────────────────▶│                   │                   │
       │                   │  4. Update        │                   │
       │                   │     is_dispatched │                   │
       │                   │──────────────────▶│                   │
       │                   │                   │                   │
       │                   │                   │  5. Notifikasi    │
       │                   │                   │◀──────────────────│
       │                   │                   │                   │
       │                   │                   │   6. Kirim Notif │
       │                   │                   │─────────────────▶│
       │                   │                   │                   │
       │                   │                   │   7. Update      │
       │                   │                   │     Status        │
       │                   │◀───────────────────│───────────────────│
```

### 5.3 Flow Penyelesaian Keluhan

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Admin     │     │   Sistem    │     │   Database  │     │  Telegram   │
│  Bidang    │     │             │     │             │     │    Bot      │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       │  1. Ubah Status   │                   │                   │
       │     ke Selesai    │                   │                   │
       │──────────────────▶│                   │                   │
       │                   │  2. Update Status │                   │
       │                   │     & selesai_at   │                   │
       │                   │──────────────────▶│                   │
       │                   │                   │                   │
       │                   │  3. Trigger        │                   │
       │                   │     Notification   │                   │
       │                   │◀───────────────────│                   │
       │                   │                   │                   │
       │                   │  4. Kirim Notif   │                   │
       │                   │     Status Baru    │                   │
       │                   │──────────────────▶│                   │
       │                   │                   │                   │
       │  5. Konfirmasi    │                   │                   │
       │◀──────────────────│                   │                   │
```

---

## 6. TEKNOLOGI YANG DIGUNAKAN

### 6.1 Teknologi Utama

| Komponen | Teknologi | Versi |
|----------|-----------|-------|
| Backend Framework | Django | 6.0.2 |
| Database | SQLite3 | - |
| Bot Framework | python-telegram-bot | - |
| Frontend | HTML/CSS | - |
| Server | Django Development Server | - |

### 6.2 Dependencies

```
Django>=6.0
python-telegram-bot
requests
asgiref
```

### 6.3 Konfigurasi Environment

```
SECRET_KEY: django-insecure-ganti-dengan-random-string-anda
DEBUG: True
ALLOWED_HOSTS: *
TIME_ZONE: Asia/Jakarta
LANGUAGE_CODE: id-id
TELEGRAM_TOKEN: 8271645073:AAEQpNuAFi-kvfP7dAsNSB4f47CvV6VxMA
```

---

## 7. STRUKTUR PROJECT

```
Support_maintanance_DiskominfoSWL/
├── bot.py                          # Telegram Bot Handler
├── manage.py                       # Django Management
├── db.sqlite3                      # Database SQLite
├── Readme.MD                       # Dokumen Rancang Bangun
│
├── keluhan/                        # Django App - Keluhan
│   ├── __init__.py
│   ├── admin.py                   # Konfigurasi Admin
│   ├── apps.py
│   ├── models.py                  # Model Database
│   ├── signals.py
│   ├── tests.py
│   ├── urls.py
│   └── migrations/                 # Database Migrations
│       ├── 0001_initial.py
│       ├── 0002_...
│       └── 0012_...
│
├── kominfo_webproject/             # Django Project
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                # Konfigurasi Django
│   ├── urls.py                    # URL Routing
│   ├── views.py                   # Views
│   └── wsgi.py
│
├── static/                        # Static Files
│   └── images/
│       ├── alur.png               # Flowchart Tutorial
│       ├── bg-tech.jpg            # Background Image
│       └── logo-kominfo.png      # Logo
│
└── templates/                     # HTML Templates
    ├── landing.html               # Landing Page
    └── admin/
        ├── deleted_history.html  # Recycle Bin
        ├── index.html            # Dashboard
        └── tutorial.html         # Tutorial Page
```

---

## 8. KEAMANAN

### 8.1 Keamanan Aplikasi
- Django built-in CSRF protection
- Session-based authentication
- Role-based access control (RBAC)
- Password validation Django

### 8.2 Keamanan Data
- Soft delete (data tidak dihapus permanen)
- Tracking pengiriman laporan (dikirim_oleh, dikirim_pada)
- Logging aktivitas pengguna

### 8.3 Rekomendasi Keamanan
1. Ganti SECRET_KEY dengan random string yang aman
2. Atur DEBUG = False di production
3. Batasi ALLOWED_HOSTS sesuai domain
4. Gunakan HTTPS di production
5. Gunakan database PostgreSQL/MySQL di production
6. Ganti token Telegram dengan yang baru
7. Implementasi rate limiting untuk bot

---

## 9.Endpoint DAN URL

### 9.1 URL Patterns

| URL | View | Keterangan |
|-----|------|------------|
| / | landing | Landing Page |
| /admin/ | dashboard | Admin Panel |
| /tutorial/ | tutorial | Halaman Tutorial |

### 9.2 Telegram Bot Commands

| Command | Deskripsi |
|---------|-----------|
| /start | Memulai bot |
| /keluhan | Ajukan keluhan |
| /sekretaris | Pilih bidang Sekretaris |
| /administrasi_umum | Pilih bidang Adm Umum |
| /administrasi_keuangan | Pilih bidang Adm Keuangan |
| /layanan_egov | Pilih bidang E-Government |
| /informasi_komunikasi | Pilih bidang Infokom |

---

## 10. PENUTUP

### 10.1 Kesimpulan
Sistem Informasi Pengelolaan Keluhan dan Feedback Diskominfo Sawahlunto merupakan solusi digital yang efektif untuk mengelola keluhan masyarakat. Dengan terintegrasi Telegram Bot, sistem ini memberikan kemudahan akses bagi masyarakat untuk menyampaikan aspirasi mereka. Dashboard admin yang komprehensif memudahkan petugas dalam mengelola dan memantau keluhan secara real-time.

### 10.2 Pengembangan Lanjutan
1. **Mobile Application** - Aplikasi mobile untuk masyarakat dan admin
2. **API REST** - REST API untuk integrasi dengan sistem lain
3. **Email Notification** - Notifikasi via email
4. **File Attachment** - Dukungan lampiran file/gambar
5. **Analytics Dashboard** - Dashboard analitik yang lebih lengkap
6. **Multi-channel** - Integrasi dengan WhatsApp, LINE, dll
7. **SLA Management** - Sistem batas waktu penanganan
8. **Reporting** - Laporan berkala otomatis

---

## LAMPIRAN

### A. Cara Menjalankan Sistem

```bash
# 1. Install dependencies
pip install django python-telegram-bot requests

# 2. Jalankan migrations
python manage.py migrate

# 3. Buat superuser
python manage.py createsuperuser

# 4. Jalankan server
python manage.py runserver

# 5. Jalankan bot (terminal terpisah)
python bot.py
```

### B. Akses Sistem
- **Landing Page**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **Tutorial**: http://localhost:8000/tutorial/
- **Telegram Bot**: @KomiSwl_bot

---

*Dokumen Rancang Bangun ini dibuat berdasarkan analisis code yang ada pada project.*
*Update terakhir: 2024*

