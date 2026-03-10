from django.shortcuts import render
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from keluhan.models import Laporan


def landing(request):
    return render(request, "landing.html")


def dashboard(request):
    return HttpResponse("Dashboard berhasil berjalan 🚀")


# ===============================
# EXPORT LAPORAN KELUHAN KE PDF
# ===============================
def laporan_keluhan_pdf(request):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="laporan_keluhan.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)

    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph("LAPORAN KELUHAN KOMINFO", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1,20))

    laporan = Laporan.objects.all().order_by('-tanggal')

    data = [
        ["Tanggal", "Nama Pengirim", "Bidang", "Jenis", "Status", "Isi"]
    ]

    for item in laporan:

        tanggal = item.tanggal.strftime("%d-%m-%Y %H:%M")
        nama = item.nama_pengirim if item.nama_pengirim else "-"
        bidang = item.bidang.nama if item.bidang else "-"
        jenis = item.jenis
        status = item.status
        isi = item.isi[:50]

        data.append([tanggal, nama, bidang, jenis, status, isi])

    table = Table(data, repeatRows=1)

    table.setStyle(TableStyle([

        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),

        ('ALIGN',(0,0),(-1,-1),'CENTER'),

        ('FONTNAME', (0,0),(-1,0),'Helvetica-Bold'),

        ('BOTTOMPADDING',(0,0),(-1,0),12),

        ('BACKGROUND',(0,1),(-1,-1),colors.beige),

        ('GRID',(0,0),(-1,-1),1,colors.black)

    ]))

    elements.append(table)

    doc.build(elements)

    return response


# ===============================
# HALAMAN TUTORIAL PENGGUNA
# ===============================
def tutorial(request):
    return render(request, "admin/tutorial.html")