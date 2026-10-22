"""
Script Generator WBS (Work Breakdown Structure) untuk Soal 1b Take Home Test Cineul Technologies.
Menghasilkan dokumen resmi SOAL_1B_WBS_PROCUREMENT.xlsx dengan multi-sheet profesional & styling korporat.
"""
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def build_wbs_workbook():
    wb = openpyxl.Workbook()
    
    # Border & Styling Common
    thin_side = Side(border_style="thin", color="CBD5E1")
    cell_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
    thick_bottom_side = Side(border_style="medium", color="1E3A8A")
    header_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thick_bottom_side)

    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    header_font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")

    lvl1_fill = PatternFill(start_color="DBEAFE", end_color="DBEAFE", fill_type="solid") # Blue 100
    lvl1_font = Font(name="Segoe UI", size=9.5, bold=True, color="1E3A8A")

    lvl2_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid") # Slate 100
    lvl2_font = Font(name="Segoe UI", size=9, bold=True, color="0F172A")

    zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    white_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    regular_font = Font(name="Segoe UI", size=9, color="334155")

    success_fill = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")
    success_font = Font(name="Segoe UI", size=9, bold=True, color="065F46")

    # =========================================================================
    # SHEET 1: WBS MODUL & FITUR LENGKAP
    # =========================================================================
    ws1 = wb.active
    ws1.title = "WBS Modul & Fitur"
    ws1.views.sheetView[0].showGridLines = True

    # Title Banner
    ws1.merge_cells("A1:J1")
    ws1["A1"] = "WORK BREAKDOWN STRUCTURE (WBS) — SISTEM PENGADAAN BARANG & JASA (PROCUREMENT)"
    ws1["A1"].font = Font(name="Segoe UI", size=14, bold=True, color="1E3A8A")
    ws1["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws1.row_dimensions[1].height = 28

    ws1.merge_cells("A2:J2")
    ws1["A2"] = "Perusahaan: Cineul Technologies | Proyek: Enterprise Procurement Web App (Python Flask & SQLite) | Scope: Request s/d Fisik Gudang"
    ws1["A2"].font = Font(name="Segoe UI", size=9.5, italic=True, color="475569")
    ws1["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws1.row_dimensions[2].height = 20

    ws1.row_dimensions[3].height = 10 # Spacer

    headers_ws1 = [
        "WBS Code",
        "Nama Modul / Fitur / Komponen Kerja",
        "Tingkat (Level)",
        "Deskripsi Fungsional & Spesifikasi Teknis",
        "Role Penanggung Jawab",
        "Source Code & Berkas Acuan",
        "Fitur Unggulan / AI Assistant",
        "Keluaran (Deliverable Output)",
        "Bobot (%)",
        "Status Kesiapan"
    ]

    ws1.row_dimensions[4].height = 28
    for col_idx, h in enumerate(headers_ws1, 1):
        c = ws1.cell(row=4, column=col_idx, value=h)
        c.fill = header_fill
        c.font = header_font
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = header_border

    # Data WBS Lengkap 7 Modul Utama (Level 1 s/d Level 3)
    wbs_rows = [
        # 1.0 MODUL AUTENTIKASI & RBAC
        ("1.0", "MODUL AUTENTIKASI, KEAMANAN & RBAC", "Level 1 (Modul)", "Sistem manajemen akses terpusat berbasis 5 hak akses peran (Role-Based Access Control)", "System Admin", "app.py, models.py, base.html", "Session Guard & Cookie Security", "Sistem Login Terlindungi & Middleware RBAC", "10%", "Selesai (100%)"),
        ("1.1", "Portal Login & Halaman Masuk Terpadu", "Level 2 (Fitur)", "Halaman login dengan infografis alur sirkular interaktif 4-tahapan & verifikasi anti-bot human check", "Semua Role", "templates/auth/login.html, app.py:login()", "Circular Infographic & Human Anti-Bot", "Form Autentikasi Modern Bebas Brute Force", "4%", "Selesai (100%)"),
        ("1.2", "Pemisahan Hak Akses Multi-Peran (RBAC)", "Level 2 (Fitur)", "Proteksi decorator @role_required untuk 5 roles: Requester, Approver, Purchasing, Warehouse, Admin", "System Admin", "app.py:role_required()", "Role-Based Endpoint Protection", "Hak Akses Menu & Routing Terisolasi Aman", "3%", "Selesai (100%)"),
        ("1.3", "Manajemen Akun & Modal Profil Pengguna", "Level 2 (Fitur)", "Pengelolaan kredensial terenkripsi (PBKDF2 SHA256), modal edit profil, nama, email & ganti password", "Semua Role", "templates/base.html, app.py:update_profile()", "User Profile Modal & Password Encryptor", "Data Master Pengguna & Audit Identitas", "3%", "Selesai (100%)"),

        # 2.0 MODUL PURCHASE REQUISITION (PR)
        ("2.0", "MODUL PURCHASE REQUISITION (PR)", "Level 1 (Modul)", "Siklus awal permohonan pengadaan barang/jasa dari divisi pemohon hingga submit dokumen", "Requester", "app.py, models.py, templates/pr/*", "Dynamic Multi-Item Grid & AI Catalog Scan", "Dokumen Elektronik PR & Database Relasional", "20%", "Selesai (100%)"),
        ("2.1", "Formulir Pengajuan Permohonan PR Baru", "Level 2 (Fitur)", "Formulir interaktif dengan penomoran unik otomatis format resmi (PR/YYYY/MM/XXXX)", "Requester", "templates/pr/create.html, app.py:pr_create()", "Auto-Generate Nomor Registrasi PR", "Header Dokumen Permohonan Pengadaan", "4%", "Selesai (100%)"),
        ("2.2", "Grid Multi-Item Dinamis & Live Calculator", "Level 2 (Fitur)", "Tambah/hapus baris item kebutuhan tanpa reload, live calculation subtotal dan grand total anggaran", "Requester", "templates/pr/create.html, static/js/script.js", "Real-Time Subtotal & Total Estimator", "Tabel Item Kebutuhan (Spek, Qty, Harga)", "5%", "Selesai (100%)"),
        ("2.3", "AI Vision: Smart Catalog & Brosur Scanner", "Level 2 (Fitur)", "Ekstraksi OCR otomatis dari foto brosur/katalog/nota toko langsung mengisi tabel baris item PR", "Requester", "app.py:ai_scan_pr_catalog(), templates/pr/create.html", "AI Computer Vision Scanner (Fitur Plus)", "Input Otomatis Multi-Item via AI Vision", "4%", "Selesai (100%)"),
        ("2.4", "Template Cepat Kebutuhan (Quick Suggestion Tags)", "Level 2 (Fitur)", "Preset satu-klik item pengadaan populer (Laptop ThinkPad, Monitor 4K, ATK PaperOne)", "Requester", "templates/pr/create.html", "One-Click Item Recommendation Chips", "Efisiensi Input Form Permohonan", "2%", "Selesai (100%)"),
        ("2.5", "Monitoring Status PR & Live Search Filters", "Level 2 (Fitur)", "Filter pills status (Semua, Menunggu, Disetujui, Ditolak, PO Terbit) dan pencarian instan", "Requester", "templates/pr/list.html, app.py:pr_list()", "Filter Pills & Live Client-side Search", "Daftar Riwayat Permohonan Terstruktur", "3%", "Selesai (100%)"),
        ("2.6", "Slip Dokumen Resmi PR Siap Cetak (A4)", "Level 2 (Fitur)", "Detail dokumen PR dengan Kop Surat formal, rekam jejak status, dan tanda tangan pemohon", "Requester / Approver", "templates/pr/detail.html", "Kop Surat Formal & Status Stampel", "Lembar Bukti Pengajuan PR Standar A4", "2%", "Selesai (100%)"),

        # 3.0 MODUL OTORISASI & APPROVAL WORKFLOW
        ("3.0", "MODUL OTORISASI & APPROVAL WORKFLOW", "Level 1 (Modul)", "Mekanisme tata kelola dan persetujuan anggaran pengadaan oleh pimpinan departemen", "Approver", "app.py, models.py, templates/approval/*", "Priority Queue & Real-Time Decision Audit", "Keputusan Otorisasi & Log Audit Pimpinan", "15%", "Selesai (100%)"),
        ("3.1", "Antrean PR Prioritas Menunggu Otorisasi", "Level 2 (Fitur)", "Dashboard antrean permohonan PR dengan highlight tanggal kebutuhan dan indikator urgensi", "Approver", "templates/approval/list.html, app.py:approval_list()", "Urgency Badge & Priority Queue List", "Daftar PR Menunggu Persetujuan Pimpinan", "4%", "Selesai (100%)"),
        ("3.2", "Peninjauan Rincian Teknis & Anggaran", "Level 2 (Fitur)", "Lembar evaluasi spesifikasi barang, kewajaran estimasi harga pasar, dan total pagu belanja", "Approver", "templates/approval/review.html, app.py:approval_review()", "Comparative Price & Specs Breakdown", "Review Objektif Dokumen Pengadaan", "4%", "Selesai (100%)"),
        ("3.3", "Eksekusi Keputusan Otorisasi (Approve / Reject)", "Level 2 (Fitur)", "Tombol eksekusi otorisasi pimpinan wajib menyertakan catatan evaluasi atau alasan penolakan", "Approver", "app.py:approval_action(), templates/approval/review.html", "SweetAlert2 Confirmation & Mandatory Notes", "Status Approval Resmi & Tanggal Otorisasi", "4%", "Selesai (100%)"),
        ("3.4", "Notifikasi Real-Time Feedback Status PR", "Level 2 (Fitur)", "Notifikasi status instan kepada Requester bila pengajuan disetujui atau ditolak pimpinan", "Approver / Requester", "templates/base.html, app.py:flash()", "Flash Feedback & Status Banner Alert", "Transparansi Alur Otorisasi Internal", "3%", "Selesai (100%)"),

        # 4.0 MODUL PURCHASE ORDER (PO) & REKANAN VENDOR
        ("4.0", "MODUL PURCHASE ORDER (PO) & REKANAN VENDOR", "Level 1 (Modul)", "Penerbitan surat pesanan resmi kepada rekanan vendor berdasarkan PR yang telah disetujui", "Purchasing", "app.py, models.py, templates/po/*", "AI Quotation OCR, Terms Sourcing & Legal Print", "Dokumen Kontrak PO & Perjanjian Legal Vendor", "20%", "Selesai (100%)"),
        ("4.1", "Antrean PR Siap Diterbitkan Menjadi PO", "Level 2 (Fitur)", "Daftar dokumen PR berstatus Approved yang siap diproses untuk penetapan rekanan vendor", "Purchasing", "templates/po/list.html, app.py:po_list()", "Auto-Sourcing Eligible PR Queue", "Daftar Seleksi PR Terotorisasi", "3%", "Selesai (100%)"),
        ("4.2", "Formulir Penerbitan Kontrak PO Baru", "Level 2 (Fitur)", "Formulir kontrak pesanan resmi dengan nomor registrasi unik otomatis (PO/YYYY/MM/XXXX)", "Purchasing", "templates/po/create.html, app.py:po_create()", "Auto-Generate Nomor Kontrak PO", "Header Dokumen Purchase Order", "3%", "Selesai (100%)"),
        ("4.3", "AI Vision: Smart Vendor Quotation Scanner", "Level 2 (Fitur)", "Ekstraksi OCR foto/scan surat penawaran resmi vendor otomatis mengisi data profil & syarat bayar", "Purchasing", "app.py:ai_scan_vendor_quotation(), templates/po/create.html", "AI Computer Vision Quotation (Fitur Plus)", "Pengisian Cepat Rekanan Vendor via AI", "4%", "Selesai (100%)"),
        ("4.4", "Quick Auto-Fill Rekanan Vendor Terdaftar", "Level 2 (Fitur)", "Pilihan cepat rekanan resmi (PT Solusi Mitra Informatika, CV ATK Berkah, PT Triputra Daya)", "Purchasing", "templates/po/create.html", "Vendor Profile Presets One-Click", "Otomasi Input Identitas Rekanan", "2%", "Selesai (100%)"),
        ("4.5", "Negosiasi Harga Deal & Live Recalculate PO", "Level 2 (Fitur)", "Penyesuaian harga deal satuan dengan kalkulasi otomatis subtotal dan total nilai kontrak PO", "Purchasing", "templates/po/create.html, static/js/script.js", "Live Recalculate Subtotal & Grand Total", "Tabel Harga Kesepakatan Final Pesanan", "4%", "Selesai (100%)"),
        ("4.6", "Cetak Slip PO Legal Standar A4 Resmi", "Level 2 (Fitur)", "Format cetak PO ber-Kop Surat Perusahaan, Cap Stempel Digital, & 3 Kolom Tanda Tangan Legal", "Purchasing / Vendor", "templates/po/detail.html, static/css/style.css", "Corporate Letterhead, Digital Stamp & 3-Sign", "Surat Pesanan Legal Siap Kirim ke Vendor", "4%", "Selesai (100%)"),

        # 5.0 MODUL GOODS RECEIPT (GR) & FISIK GUDANG
        ("5.0", "MODUL GOODS RECEIPT (GR) & FISIK GUDANG", "Level 1 (Modul)", "Verifikasi penerimaan fisik barang dan surat jalan kurir di gudang (Titik Akhir Scope Pengadaan)", "Warehouse", "app.py, models.py, templates/gr/*", "AI Delivery Order OCR & Physical Tagging", "Berita Acara Penerimaan Barang (GR Slip)", "20%", "Selesai (100%)"),
        ("5.1", "Monitoring Kedatangan Fisik Kargo Logistik", "Level 2 (Fitur)", "Pemantauan daftar PO berstatus aktif (Issued) yang sedang dalam pengiriman ekspedisi ke gudang", "Warehouse", "templates/gr/list.html, app.py:gr_list()", "Inbound Cargo Tracker & PO Reference Card", "Antrean Penerimaan Fisik Kargo", "3%", "Selesai (100%)"),
        ("5.2", "AI Computer Vision: Smart Scanner Surat Jalan (DO)", "Level 2 (Fitur)", "Pemindaian dokumen Delivery Order (DO) kurir untuk ekstrak nomor DO, tanggal & kondisi segel", "Warehouse", "app.py:ai_scan_delivery_order(), templates/gr/create.html", "AI Computer Vision DO Scanner (Fitur Plus)", "Ekstraksi Otomatis Surat Jalan Vendor", "5%", "Selesai (100%)"),
        ("5.3", "Inspeksi Fisik: Cek Kuantitas & Tagging Kondisi", "Level 2 (Fitur)", "Verifikasi kuantitas fisik riil vs PO serta penandaan kondisi fisik: Baik / Rusak / Salah Tipe", "Warehouse", "templates/gr/create.html, app.py:gr_create()", "Defect & Damage Physical Tagging", "Data Verifikasi Fisik Kargo Gudang", "4%", "Selesai (100%)"),
        ("5.4", "Auto-Calculated Status Penerimaan PO", "Level 2 (Fitur)", "Sistem otomatis menetapkan status Received (Lengkap) atau Partially Received (Sebagian)", "Warehouse", "app.py:gr_create(), models.py:PurchaseOrder", "Automated Partial / Full Status Evaluator", "Update Status PO & GR Terintegrasi", "4%", "Selesai (100%)"),
        ("5.5", "Cetak Slip Bukti Serah Terima Goods Receipt", "Level 2 (Fitur)", "Pencetakan Berita Acara Penerimaan Barang standar A4 lengkap dengan Kop Surat & Tanda Tangan", "Warehouse", "templates/gr/detail.html, static/css/style.css", "Official Warehouse GR Slip & Signature Area", "Slip Legal Tanda Terima Fisik Barang", "4%", "Selesai (100%)"),

        # 6.0 MODUL ANALITIK & DASHBOARD EKSEKUTIF
        ("6.0", "MODUL ANALITIK, DASHBOARD & PELAPORAN", "Level 1 (Modul)", "Pusat informasi metrik KPI, statistik pengadaan, grafik real-time, dan transparansi alur transaksi", "Semua Role", "templates/dashboard/*, app.py:dashboard()", "Role-Tailored KPI Cards & Chart.js Real-time", "Dasbor Eksekutif & Ringkasan Performa", "10%", "Selesai (100%)"),
        ("6.1", "Role-Tailored Dashboard Eksekutif", "Level 2 (Fitur)", "Metrik statistik disesuaikan khusus untuk tiap peran: Requester, Approver, Purchasing, Warehouse, Admin", "Semua Role", "templates/dashboard/index.html", "Custom Dynamic Metrics per User Role", "Panel Monitoring Khusus Masing-masing Role", "4%", "Selesai (100%)"),
        ("6.2", "Visualisasi Grafik Real-Time (Chart.js)", "Level 2 (Fitur)", "Grafik status pengadaan dan diagram batang tren realisasi belanja anggaran per departemen", "Approver / Admin", "templates/dashboard/index.html, Chart.js", "Interactive Donut & Bar Charts", "Visualisasi Tren Pengadaan Organisasi", "3%", "Selesai (100%)"),
        ("6.3", "Audit Trail & Pelacakan Alur Dokumen", "Level 2 (Fitur)", "Pelacakan hulu-ke-hilir siklus pengadaan (PR -> Approval -> PO -> GR) secara transparan", "Admin / Auditor", "app.py, templates/dashboard/index.html", "End-to-End Transaction Traceability", "Log Riwayat Transaksi Lengkap", "3%", "Selesai (100%)"),

        # 7.0 FITUR NILAI PLUS: AI VISION PROCUREMENT SUITE
        ("7.0", "FITUR OPSIONAL NILAI PLUS: AI VISION SUITE", "Level 1 (Modul)", "Penerapan Computer Vision & AI Model terintegrasi di 3 titik proses pengadaan untuk seluruh role", "Cross-Role", "app.py, templates/pr/*, templates/po/*, templates/gr/*", "Multi-Stage Computer Vision & OCR Ecosystem", "Ekosistem AI Pengadaan Modern", "Nilai Plus", "Selesai (100%)"),
        ("7.1", "AI Smart Catalog & Brosur Scanner (Requester)", "Level 2 (Fitur)", "Ekstraksi multi-item otomatis dari foto brosur/katalog toko langsung mengisi tabel baris item PR", "Requester", "app.py:ai_scan_pr_catalog(), templates/pr/create.html", "AI Multi-Item Catalog Extractor", "Otomasi Form PR Berbasis AI Vision", "Nilai Plus", "Selesai (100%)"),
        ("7.2", "AI Vendor Quotation Scanner (Purchasing)", "Level 2 (Fitur)", "Ekstraksi otomatis lembar surat penawaran rekanan vendor mengisi profil vendor & payment terms PO", "Purchasing", "app.py:ai_scan_vendor_quotation(), templates/po/create.html", "AI Quotation OCR Extractor", "Otomasi Form PO Berbasis AI Vision", "Nilai Plus", "Selesai (100%)"),
        ("7.3", "AI Delivery Order Scanner (Warehouse)", "Level 2 (Fitur)", "Ekstraksi nomor DO & verifikasi kondisi fisik segel kemasan barang dari surat jalan kurir", "Warehouse", "app.py:ai_scan_delivery_order(), templates/gr/create.html", "AI DO & Packaging Integrity Checker", "Otomasi Form GR Berbasis AI Vision", "Nilai Plus", "Selesai (100%)")
    ]

    current_r = 5
    for row_idx, r_data in enumerate(wbs_rows, 1):
        ws1.row_dimensions[current_r].height = 24
        is_lvl1 = "Level 1" in r_data[2]
        is_lvl2 = "Level 2" in r_data[2]

        for col_idx, val in enumerate(r_data, 1):
            cell = ws1.cell(row=current_r, column=col_idx, value=val)
            cell.border = cell_border

            # Styling berdasarkan level hirarki
            if is_lvl1:
                cell.fill = lvl1_fill
                cell.font = lvl1_font
            elif is_lvl2:
                if row_idx % 2 == 0:
                    cell.fill = lvl2_fill
                else:
                    cell.fill = white_fill
                cell.font = lvl2_font if col_idx in [1, 2] else regular_font
            else:
                cell.fill = zebra_fill if row_idx % 2 == 0 else white_fill
                cell.font = regular_font

            # Status column badge style
            if col_idx == 10:
                cell.fill = success_fill
                cell.font = success_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx in [1, 3, 5, 9]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

        current_r += 1

    # Widths untuk Sheet 1
    col_widths_ws1 = {
        1: 13,  # WBS Code
        2: 36,  # Nama Fitur
        3: 16,  # Tingkat
        4: 48,  # Deskripsi
        5: 20,  # Role
        6: 32,  # Source Code
        7: 28,  # Fitur AI
        8: 34,  # Deliverable
        9: 12,  # Bobot
        10: 16  # Status
    }
    for col_idx, w in col_widths_ws1.items():
        ws1.column_dimensions[get_column_letter(col_idx)].width = w

    # =========================================================================
    # SHEET 2: MATRIKS HAK AKSES PERAN (RBAC ACCESS MATRIX)
    # =========================================================================
    ws2 = wb.create_sheet(title="Matriks Hak Akses (RBAC)")
    ws2.views.sheetView[0].showGridLines = True

    ws2.merge_cells("A1:G1")
    ws2["A1"] = "MATRIKS HAK AKSES & OTORITAS PENGGUNA (ROLE-BASED ACCESS CONTROL)"
    ws2["A1"].font = Font(name="Segoe UI", size=13, bold=True, color="1E3A8A")
    ws2["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws2.row_dimensions[1].height = 26

    ws2.merge_cells("A2:G2")
    ws2["A2"] = "Pemetaan 5 Peran: Requester, Approver, Purchasing, Warehouse, dan System Administrator"
    ws2["A2"].font = Font(name="Segoe UI", size=9.5, italic=True, color="475569")
    ws2["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws2.row_dimensions[2].height = 20

    ws2.row_dimensions[3].height = 10

    headers_ws2 = [
        "Modul & Fungsi Sistem",
        "Requester (Pemohon)",
        "Approver (Dept Head)",
        "Purchasing (Sourcing)",
        "Warehouse (Gudang)",
        "System Administrator",
        "Keterangan Kebijakan Tata Kelola"
    ]

    ws2.row_dimensions[4].height = 26
    for col_idx, h in enumerate(headers_ws2, 1):
        c = ws2.cell(row=4, column=col_idx, value=h)
        c.fill = header_fill
        c.font = header_font
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = header_border

    rbac_matrix_data = [
        ("Login Portal & Autentikasi Human Check", "Bisa Akses", "Bisa Akses", "Bisa Akses", "Bisa Akses", "Bisa Akses", "Semua user wajib verifikasi kredensial"),
        ("Edit Profil Akun & Ganti Password", "Bisa Akses", "Bisa Akses", "Bisa Akses", "Bisa Akses", "Bisa Akses", "Setiap user mengelola kredensial sendiri"),
        ("Buat Purchase Requisition (PR Baru)", "FULL AKSES (CREATE)", "Read Only", "Read Only", "Tidak Ada Akses", "Monitoring", "Hak eksklusif divisi pemohon barang"),
        ("AI Smart Catalog & Brosur Scanner", "FULL AKSES (AI SCAN)", "Read Only", "Read Only", "Tidak Ada Akses", "Monitoring", "Membantu ekstraksi barang di form PR"),
        ("Tinjau & Otorisasi PR (Approve / Reject)", "Tidak Ada Akses", "FULL AKSES (APPROVE)", "Read Only", "Tidak Ada Akses", "Monitoring", "Kewenangan otorisasi pimpinan divisi"),
        ("Terbitkan Purchase Order Resmi (PO)", "Tidak Ada Akses", "Read Only", "FULL AKSES (CREATE)", "Read Only", "Monitoring", "Hak negosiasi & kontrak rekanan vendor"),
        ("AI Vendor Quotation OCR Scanner", "Tidak Ada Akses", "Read Only", "FULL AKSES (AI SCAN)", "Tidak Ada Akses", "Monitoring", "Ekstraksi otomatis surat penawaran vendor"),
        ("Cetak Lembar PO Legal Standar A4", "Read Only", "Read Only", "FULL CETAK (PRINT)", "Read Only", "FULL CETAK (PRINT)", "Format resmi dengan Kop Surat & Cap"),
        ("Terima Barang Fisik & Goods Receipt (GR)", "Tidak Ada Akses", "Tidak Ada Akses", "Read Only", "FULL AKSES (CREATE)", "Monitoring", "Verifikasi fisik kargo tiba di gudang"),
        ("AI Delivery Order (DO) Scanner", "Tidak Ada Akses", "Tidak Ada Akses", "Read Only", "FULL AKSES (AI SCAN)", "Monitoring", "Membaca nomor surat jalan & segel paket"),
        ("Cetak Slip Bukti Penerimaan Barang (GR)", "Tidak Ada Akses", "Tidak Ada Akses", "Read Only", "FULL CETAK (PRINT)", "FULL CETAK (PRINT)", "Berita Acara tanda terima kargo gudang"),
        ("Dashboard Dinamis Khusus Role", "KPI Pemohon", "KPI Otorisasi", "KPI Sourcing & PO", "KPI Logistik & GR", "Global Enterprise KPI", "Tampilan menyesuaikan peran yang login"),
        ("Manajemen Pengguna & Database Seeder", "Tidak Ada Akses", "Tidak Ada Akses", "Tidak Ada Akses", "Tidak Ada Akses", "FULL KONTROL ADMIN", "Pengaturan sistem dan keamanan data")
    ]

    for row_idx, r in enumerate(rbac_matrix_data, 5):
        ws2.row_dimensions[row_idx].height = 22
        for col_idx, val in enumerate(r, 1):
            cell = ws2.cell(row=row_idx, column=col_idx, value=val)
            cell.border = cell_border
            if row_idx % 2 == 0:
                cell.fill = zebra_fill
            else:
                cell.fill = white_fill

            if "FULL" in val:
                cell.fill = success_fill
                cell.font = Font(name="Segoe UI", size=8.5, bold=True, color="065F46")
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif "Bisa" in val or "KPI" in val:
                cell.fill = lvl1_fill
                cell.font = Font(name="Segoe UI", size=8.5, bold=True, color="1E3A8A")
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif "Read" in val:
                cell.font = Font(name="Segoe UI", size=8.5, italic=True, color="475569")
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif "Tidak" in val:
                cell.font = Font(name="Segoe UI", size=8.5, color="94A3B8")
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.font = Font(name="Segoe UI", size=9, bold=(col_idx == 1), color="0F172A")
                cell.alignment = Alignment(horizontal="left", vertical="center")

    col_widths_ws2 = {1: 36, 2: 24, 3: 24, 4: 24, 5: 24, 6: 24, 7: 38}
    for col_idx, w in col_widths_ws2.items():
        ws2.column_dimensions[get_column_letter(col_idx)].width = w

    # =========================================================================
    # SHEET 3: SPESIFIKASI TEKNIS & LINGKUP (SCOPE OF WORK)
    # =========================================================================
    ws3 = wb.create_sheet(title="Spesifikasi & Scope")
    ws3.views.sheetView[0].showGridLines = True

    ws3.merge_cells("A1:E1")
    ws3["A1"] = "RINGKASAN SPESIFIKASI TEKNIS & BATASAN RUANG LINGKUP SISTEM"
    ws3["A1"].font = Font(name="Segoe UI", size=13, bold=True, color="1E3A8A")
    ws3["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws3.row_dimensions[1].height = 26

    ws3.merge_cells("A2:E2")
    ws3["A2"] = "Take Home Programming Test Software Engineer — Cineul Technologies"
    ws3["A2"].font = Font(name="Segoe UI", size=9.5, italic=True, color="475569")
    ws3["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws3.row_dimensions[2].height = 20

    ws3.row_dimensions[3].height = 10

    headers_ws3 = ["Kategori", "Ketentuan Lembar Soal", "Implementasi Nyata pada Aplikasi", "Kesesuaian", "Catatan Teknis Arsitektur"]
    ws3.row_dimensions[4].height = 26
    for col_idx, h in enumerate(headers_ws3, 1):
        c = ws3.cell(row=4, column=col_idx, value=h)
        c.fill = header_fill
        c.font = header_font
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = header_border

    scope_data = [
        ("Pilihan Aplikasi", "Memilih 1 dari 2 (Helpdesk / Procurement)", "Aplikasi Procurement (Pengadaan Terpadu)", "100% Sesuai", "Menangani alur end-to-end pengadaan"),
        ("Bahasa Pemrograman", "Wajib menggunakan Python", "Python 3.9+ & Framework Flask 3.x", "100% Sesuai", "Kode bersih, modular & standar PEP 8"),
        ("Basis Data", "Database sqlite / PostgreSQL", "SQLite Relasional (ACID Compliant)", "100% Sesuai", "Integrasi ketat PRAGMA foreign_keys = ON"),
        ("Batasan Lingkup (In-Scope)", "Request sampai barang/jasa sampai di gudang", "PR -> Approval -> PO -> Goods Receipt (GR)", "100% Sesuai", "Titik akhir adalah tanda terima fisik di gudang"),
        ("Batasan Lingkup (Out-of-Scope)", "Bukan aplikasi gudang internal", "Tidak mengelola bin slotting & kartu stok internal", "100% Sesuai", "Sesuai batasan tegas spesifikasi soal"),
        ("Batasan Lingkup (Out-of-Scope)", "Bukan aplikasi pembayaran", "Tidak ada modul disbursement/kas/bank", "100% Sesuai", "Sesuai batasan tegas spesifikasi soal"),
        ("Soal 1a: BPMN Swimlane", "Swimlane BPMN, role > 2, direkomendasikan draw.io", "Draw.io Vertikal 5 Roles (SOAL_1A_BPMN_SWIMLANE.drawio)", "100% Selesai", "Alur vertikal panjang ke bawah & siap export PDF"),
        ("Soal 1b: WBS Modul & Fitur", "Work Breakdown Structure dalam file Excel", "Excel Multi-Sheet (SOAL_1B_WBS_PROCUREMENT.xlsx)", "100% Selesai", "Lengkap dengan WBS, Matriks RBAC & Spek"),
        ("Fitur Opsional (Nilai Plus)", "Salah satu tahapan menggunakan Computer Vision/AI", "AI Vision Suite di 3 Tahapan (PR, PO, GR)", "Melampaui Target", "Semua role merasakan manfaat nyata AI"),
        ("Format Cetak Dokumen", "Dokumen transaksi resmi pengadaan", "Standar Cetak A4, Kop Surat, Stempel Digital, 3 Tanda Tangan", "Standar Industri", "Dokumen PO dan GR siap audit legal")
    ]

    for row_idx, r in enumerate(scope_data, 5):
        ws3.row_dimensions[row_idx].height = 22
        for col_idx, val in enumerate(r, 1):
            cell = ws3.cell(row=row_idx, column=col_idx, value=val)
            cell.border = cell_border
            if row_idx % 2 == 0:
                cell.fill = zebra_fill
            else:
                cell.fill = white_fill

            if col_idx == 4:
                cell.fill = success_fill
                cell.font = success_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx in [1, 2]:
                cell.font = Font(name="Segoe UI", size=9, bold=(col_idx == 1), color="0F172A")
                cell.alignment = Alignment(horizontal="left", vertical="center")
            else:
                cell.font = Font(name="Segoe UI", size=9, color="334155")
                cell.alignment = Alignment(horizontal="left", vertical="center")

    col_widths_ws3 = {1: 24, 2: 36, 3: 40, 4: 18, 5: 38}
    for col_idx, w in col_widths_ws3.items():
        ws3.column_dimensions[get_column_letter(col_idx)].width = w

    os.makedirs("docs", exist_ok=True)
    out_xlsx = os.path.join("docs", "SOAL_1B_WBS_PROCUREMENT.xlsx")
    wb.save(out_xlsx)
    print(f"Berhasil menghasilkan Excel WBS profesional: {out_xlsx}")

if __name__ == "__main__":
    build_wbs_workbook()
