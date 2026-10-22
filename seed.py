from datetime import date, datetime, timedelta
from flask import Flask
from models import db, User, PurchaseRequisition, PRItem, PurchaseOrder, POItem, GoodsReceipt, GRItem
from database import init_app_db

def seed_database():
    app = Flask(__name__)
    init_app_db(app)

    with app.app_context():
        # Hapus data lama dan buat tabel baru
        print("Mengatur ulang tabel database...")
        db.drop_all()
        db.create_all()

        print("Menambahkan data pengguna (Users)...")
        # 1. Seed Users
        users = [
            User(
                username='requester',
                full_name='Budi Santoso',
                role='Requester',
                department='Information Technology'
            ),
            User(
                username='approver',
                full_name='Siti Rahmawati, M.T.',
                role='Approver',
                department='IT Management / Department Head'
            ),
            User(
                username='purchasing',
                full_name='Andi Wijaya',
                role='Purchasing',
                department='Procurement & Sourcing'
            ),
            User(
                username='warehouse',
                full_name='Doni Prasetyo',
                role='Warehouse',
                department='Warehouse & Logistics'
            ),
            User(
                username='admin',
                full_name='Administrator Sistem',
                role='Admin',
                department='System Administrator'
            )
        ]

        for u in users:
            if u.username == 'admin':
                u.set_password('admin123')
            else:
                u.set_password('password123')
            db.session.add(u)
        
        db.session.commit()
        print("Pengguna berhasil dibuat!")

        # Referensi user untuk data transaksi
        u_req = User.query.filter_by(username='requester').first()
        u_app = User.query.filter_by(username='approver').first()
        u_pur = User.query.filter_by(username='purchasing').first()
        u_wh = User.query.filter_by(username='warehouse').first()

        today = date.today()

        # ==========================================
        # 2. Contoh PR 1: Menunggu Approval (Pending)
        # ==========================================
        pr1 = PurchaseRequisition(
            pr_number='PR-2026-0001',
            requester_id=u_req.id,
            department='Information Technology',
            request_date=today - timedelta(days=2),
            required_date=today + timedelta(days=12),
            purpose='Pengadaan Laptop Developer dan Monitor untuk personil tim engineering baru kuartal 4.',
            status='Pending',
            total_estimated_amount=0.0
        )
        db.session.add(pr1)
        db.session.flush()

        pr1_items = [
            PRItem(
                pr_id=pr1.id,
                item_name='Laptop ThinkPad T14 Gen 4 Ryzen 7 / 32GB RAM',
                specification='AMD Ryzen 7 PRO, 32GB LPDDR5, 1TB NVMe SSD, 14 Inch FHD IPS',
                quantity=2,
                unit='Unit',
                estimated_price=18500000.0,
                subtotal=37000000.0
            ),
            PRItem(
                pr_id=pr1.id,
                item_name='Monitor Dell 27 Inch 4K UHD UltraSharp U2723QE',
                specification='27 Inch IPS Black 4K, USB-C Hub 90W PD, Color Accurate 98% DCI-P3',
                quantity=2,
                unit='Unit',
                estimated_price=8200000.0,
                subtotal=16400000.0
            )
        ]
        for itm in pr1_items:
            db.session.add(itm)
        pr1.calculate_total()

        # ==========================================
        # 3. Contoh PR 2: Ditolak (Rejected)
        # ==========================================
        pr2 = PurchaseRequisition(
            pr_number='PR-2026-0002',
            requester_id=u_req.id,
            department='Information Technology',
            request_date=today - timedelta(days=5),
            required_date=today + timedelta(days=7),
            purpose='Pengadaan Coffee Machine Otomatis untuk ruang pantri IT.',
            status='Rejected',
            approver_id=u_app.id,
            approval_date=datetime.now() - timedelta(days=4),
            approval_notes='Anggaran operasional pantri dialihkan untuk kebutuhan infrastruktur server terlebih dahulu.',
            total_estimated_amount=0.0
        )
        db.session.add(pr2)
        db.session.flush()

        pr2_items = [
            PRItem(
                pr_id=pr2.id,
                item_name='Espresso Coffee Machine DeLonghi Magnifica S',
                specification='Fully Automatic, 15 bar pump, integrated grinder',
                quantity=1,
                unit='Unit',
                estimated_price=9800000.0,
                subtotal=9800000.0
            )
        ]
        for itm in pr2_items:
            db.session.add(itm)
        pr2.calculate_total()

        # ==========================================
        # 4. Contoh PR 3: Disetujui (Approved) - Menunggu Pembuatan PO oleh Purchasing
        # ==========================================
        pr3 = PurchaseRequisition(
            pr_number='PR-2026-0003',
            requester_id=u_req.id,
            department='Information Technology',
            request_date=today - timedelta(days=3),
            required_date=today + timedelta(days=10),
            purpose='Penggantian UPS Server Rack Data Center yang baterainya degradasi.',
            status='Approved',
            approver_id=u_app.id,
            approval_date=datetime.now() - timedelta(days=2),
            approval_notes='Disetujui. Segera koordinasikan dengan tim Purchasing untuk PO cepat karena urgensi DC.',
            total_estimated_amount=0.0
        )
        db.session.add(pr3)
        db.session.flush()

        pr3_items = [
            PRItem(
                pr_id=pr3.id,
                item_name='APC Smart-UPS On-Line 3000VA 230V 2U Rackmount (SRT3000XLI)',
                specification='Double conversion online topology, LCD display, SmartSlot',
                quantity=2,
                unit='Unit',
                estimated_price=24500000.0,
                subtotal=49000000.0
            )
        ]
        for itm in pr3_items:
            db.session.add(itm)
        pr3.calculate_total()

        # ==========================================
        # 5. Contoh PR 4 + PO 1: PO Terbit (Issued) - Menunggu Pengiriman ke Gudang
        # ==========================================
        pr4 = PurchaseRequisition(
            pr_number='PR-2026-0004',
            requester_id=u_req.id,
            department='Information Technology',
            request_date=today - timedelta(days=7),
            required_date=today + timedelta(days=5),
            purpose='Peralatan Jaringan Switch Cisco Gigabit & Kabel LAN Cat6 Roll.',
            status='PO Created',
            approver_id=u_app.id,
            approval_date=datetime.now() - timedelta(days=6),
            approval_notes='Disetujui sesuai RKAT IT 2026.',
            total_estimated_amount=0.0
        )
        db.session.add(pr4)
        db.session.flush()

        pr4_item1 = PRItem(
            pr_id=pr4.id,
            item_name='Cisco Catalyst 2960-X 24 Port Gigabit Switch',
            specification='24x 10/100/1000 Ethernet Ports, 4x 1G SFP, LAN Base',
            quantity=2,
            unit='Unit',
            estimated_price=12000000.0,
            subtotal=24000000.0
        )
        pr4_item2 = PRItem(
            pr_id=pr4.id,
            item_name='Belden Cable UTP Cat6 305 Meter (Original)',
            specification='100% Solid Copper 23 AWG, 305m per roll',
            quantity=3,
            unit='Roll',
            estimated_price=2100000.0,
            subtotal=6300000.0
        )
        db.session.add_all([pr4_item1, pr4_item2])
        pr4.calculate_total()
        db.session.flush()

        po1 = PurchaseOrder(
            po_number='PO-2026-0001',
            pr_id=pr4.id,
            purchasing_id=u_pur.id,
            vendor_name='PT Solusi Mitra Informatika',
            vendor_address='Gedung Cyber 2 Lantai 15, Jl. HR Rasuna Said, Jakarta Selatan',
            vendor_phone='021-52908877',
            vendor_email='sales@solusimitra.co.id',
            po_date=today - timedelta(days=5),
            delivery_estimate_date=today + timedelta(days=3),
            payment_terms='Net 30 Days',
            notes='Pengiriman harap langsung ke Gudang Utama Gedung B. Melampirkan surat jalan asli dan PO copy.',
            status='Issued',
            total_amount=0.0
        )
        db.session.add(po1)
        db.session.flush()

        po1_items = [
            POItem(
                po_id=po1.id,
                pr_item_id=pr4_item1.id,
                item_name='Cisco Catalyst 2960-X 24 Port Gigabit Switch',
                specification='24x 10/100/1000 Ethernet Ports, 4x 1G SFP, LAN Base',
                quantity=2,
                unit='Unit',
                unit_price=11800000.0,
                subtotal=23600000.0
            ),
            POItem(
                po_id=po1.id,
                pr_item_id=pr4_item2.id,
                item_name='Belden Cable UTP Cat6 305 Meter (Original)',
                specification='100% Solid Copper 23 AWG, 305m per roll',
                quantity=3,
                unit='Roll',
                unit_price=2050000.0,
                subtotal=6150000.0
            )
        ]
        db.session.add_all(po1_items)
        po1.calculate_total()

        # ==========================================
        # 6. Contoh PR 5 + PO 2 + GR 1: Siklus Lengkap Sampai Goods Receipt (Received)
        # ==========================================
        pr5 = PurchaseRequisition(
            pr_number='PR-2026-0005',
            requester_id=u_req.id,
            department='Information Technology',
            request_date=today - timedelta(days=14),
            required_date=today - timedelta(days=4),
            purpose='Pengadaan Kertas HVS A4 & F4 serta Toner Printer Kantor untuk operasional bulanan.',
            status='PO Created',
            approver_id=u_app.id,
            approval_date=datetime.now() - timedelta(days=13),
            approval_notes='Approved. Prioritas pengadaan bulanan.',
            total_estimated_amount=0.0
        )
        db.session.add(pr5)
        db.session.flush()

        pr5_item1 = PRItem(
            pr_id=pr5.id,
            item_name='Kertas PaperOne A4 80gr',
            specification='Ukuran A4 210 x 297 mm, 80 gsm, 500 lembar per rim',
            quantity=20,
            unit='Rim',
            estimated_price=55000.0,
            subtotal=1100000.0
        )
        pr5_item2 = PRItem(
            pr_id=pr5.id,
            item_name='Toner HP LaserJet Original 85A (CE285A)',
            specification='Original HP Black Toner Cartridge, yield up to 1600 pages',
            quantity=4,
            unit='Unit',
            estimated_price=950000.0,
            subtotal=3800000.0
        )
        db.session.add_all([pr5_item1, pr5_item2])
        pr5.calculate_total()
        db.session.flush()

        po2 = PurchaseOrder(
            po_number='PO-2026-0002',
            pr_id=pr5.id,
            purchasing_id=u_pur.id,
            vendor_name='CV ATK Berkah Jaya Mandiri',
            vendor_address='Jl. Kramat Raya No. 44, Senen, Jakarta Pusat',
            vendor_phone='021-3908812',
            vendor_email='order@atkberkah.com',
            po_date=today - timedelta(days=10),
            delivery_estimate_date=today - timedelta(days=2),
            payment_terms='Cash On Delivery (COD)',
            notes='Karton pembungkus kertas wajib dilapisi plastik anti air.',
            status='Received',
            total_amount=0.0
        )
        db.session.add(po2)
        db.session.flush()

        po2_item1 = POItem(
            po_id=po2.id,
            pr_item_id=pr5_item1.id,
            item_name='Kertas PaperOne A4 80gr',
            specification='Ukuran A4 210 x 297 mm, 80 gsm, 500 lembar per rim',
            quantity=20,
            unit='Rim',
            unit_price=53000.0,
            subtotal=1060000.0
        )
        po2_item2 = POItem(
            po_id=po2.id,
            pr_item_id=pr5_item2.id,
            item_name='Toner HP LaserJet Original 85A (CE285A)',
            specification='Original HP Black Toner Cartridge, yield up to 1600 pages',
            quantity=4,
            unit='Unit',
            unit_price=920000.0,
            subtotal=3680000.0
        )
        db.session.add_all([po2_item1, po2_item2])
        po2.calculate_total()
        db.session.flush()

        # Buat Goods Receipt (GR) oleh Warehouse
        gr1 = GoodsReceipt(
            gr_number='GR-2026-0001',
            po_id=po2.id,
            warehouse_officer_id=u_wh.id,
            delivery_order_number='DO/BJM/2026/X/084',
            received_date=today - timedelta(days=1),
            notes='Barang telah diterima di Gudang Sentral. Seluruh segel kardus utuh dan toner original tersegel hologram.',
            status='Complete'
        )
        db.session.add(gr1)
        db.session.flush()

        gr1_item1 = GRItem(
            gr_id=gr1.id,
            po_item_id=po2_item1.id,
            quantity_received=20,
            condition_status='Baik',
            notes='20 Rim kertas HVS kondisi bersih dan kering sempurna.'
        )
        gr1_item2 = GRItem(
            gr_id=gr1.id,
            po_item_id=po2_item2.id,
            quantity_received=4,
            condition_status='Baik',
            notes='4 Unit toner bersegel resmi pabrikan HP.'
        )
        db.session.add_all([gr1_item1, gr1_item2])

        db.session.commit()
        print("Database berhasil di-seed dengan data awal!")
        print("\nAkun yang tersedia:")
        print("1. Requester  : requester  / password123")
        print("2. Approver   : approver   / password123")
        print("3. Purchasing : purchasing / password123")
        print("4. Warehouse  : warehouse  / password123")
        print("5. Admin      : admin      / admin123")

if __name__ == '__main__':
    seed_database()
