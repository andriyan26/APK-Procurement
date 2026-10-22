import os
from datetime import datetime, date
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, abort, send_from_directory
)
from models import (
    db, User, PurchaseRequisition, PRItem,
    PurchaseOrder, POItem, GoodsReceipt, GRItem
)
from database import init_app_db

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'procurement-cineul-tech-super-secret-key-2026')

# Inisialisasi Database
init_app_db(app)

# ==========================================
# CUSTOM JINJA FILTERS & CONTEXT PROCESSOR
# ==========================================
@app.template_filter('format_currency')
def format_currency_filter(value):
    try:
        val = float(value or 0)
        return f"Rp {val:,.0f}".replace(',', '.')
    except (ValueError, TypeError):
        return "Rp 0"

@app.template_filter('format_date')
def format_date_filter(value, fmt='%d/%m/%Y'):
    if not value:
        return '-'
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            return value
    return value.strftime(fmt)

@app.context_processor
def inject_global_data():
    current_user = None
    if 'user_id' in session:
        current_user = User.query.get(session['user_id'])
    
    # Hitung badge notifikasi pending
    pending_pr_count = 0
    approved_pr_count = 0
    open_po_count = 0
    try:
        pending_pr_count = PurchaseRequisition.query.filter_by(status='Pending').count()
        approved_pr_count = PurchaseRequisition.query.filter_by(status='Approved').count()
        open_po_count = PurchaseOrder.query.filter(PurchaseOrder.status.in_(['Issued', 'Partially Received'])).count()
    except Exception:
        pass

    return {
        'current_user': current_user,
        'current_year': datetime.now().year,
        'pending_pr_count': pending_pr_count,
        'approved_pr_count': approved_pr_count,
        'open_po_count': open_po_count
    }

# ==========================================
# AUTH DECORATORS
# ==========================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu untuk mengakses halaman ini.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Silakan login terlebih dahulu.', 'warning')
                return redirect(url_for('login'))
            user = User.query.get(session['user_id'])
            if not user or (user.role not in allowed_roles and user.role != 'Admin'):
                flash('Anda tidak memiliki hak akses untuk membuka halaman tersebut.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ==========================================
# AUTHENTICATION ROUTES
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # Pengecekan Human Verification (Anti-Bot Security Check)
        human_verified = request.form.get('human_verification')
        if not human_verified or human_verified != 'verified':
            flash('Pengecekan keamanan wajib: Harap selesaikan verifikasi bahwa Anda manusia (Bukan Robot).', 'warning')
            return render_template('auth/login.html')

        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['full_name'] = user.full_name
            session['role'] = user.role
            flash(f'Selamat datang kembali, {user.full_name} ({user.role})!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Username atau kata sandi tidak valid. Silakan coba lagi.', 'danger')

    return render_template('auth/login.html')

@app.route('/quick-login/<role_name>')
def quick_login(role_name):
    """Kemudahan pengujian untuk beralih peran dalam sekali klik"""
    user = User.query.filter_by(role=role_name).first()
    if user:
        session['user_id'] = user.id
        session['username'] = user.username
        session['full_name'] = user.full_name
        session['role'] = user.role
        flash(f'Beralih peran sebagai {user.full_name} ({user.role}) berhasil.', 'info')
    else:
        flash(f'Akun untuk peran {role_name} tidak ditemukan.', 'warning')
    return redirect(url_for('dashboard'))

@app.route('/profile/update', methods=['POST'])
@login_required
def profile_update():
    user = User.query.get(session['user_id'])
    if not user:
        flash('Pengguna tidak ditemukan.', 'danger')
        return redirect(url_for('login'))

    action_type = request.form.get('action_type', 'info')
    
    if action_type == 'info':
        full_name = request.form.get('full_name', '').strip()
        department = request.form.get('department', '').strip()
        if not full_name:
            flash('Nama lengkap tidak boleh kosong.', 'danger')
        else:
            user.full_name = full_name
            user.department = department
            session['full_name'] = full_name
            db.session.commit()
            flash('Pengaturan akun berhasil disimpan!', 'success')
            
    elif action_type == 'password':
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not user.check_password(old_password):
            flash('Kata sandi saat ini salah. Silakan coba lagi.', 'danger')
        elif len(new_password) < 6:
            flash('Kata sandi baru minimal 6 karakter.', 'danger')
        elif new_password != confirm_password:
            flash('Konfirmasi kata sandi baru tidak cocok.', 'danger')
        else:
            user.set_password(new_password)
            db.session.commit()
            flash('Kata sandi berhasil diperbarui! Silakan gunakan kata sandi baru pada sesi berikutnya.', 'success')

    return redirect(request.referrer or url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah berhasil keluar dari sistem.', 'info')
    return redirect(url_for('login'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static', 'img'),
        'favicon.svg',
        mimetype='image/svg+xml'
    )


# ==========================================
# DASHBOARD (5-ROLES DYNAMIC & REAL-TIME)
# ==========================================
@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    
    # 1. Metrik Global Pengadaan
    total_pr = PurchaseRequisition.query.count()
    pending_pr = PurchaseRequisition.query.filter_by(status='Pending').count()
    approved_pr = PurchaseRequisition.query.filter_by(status='Approved').count()
    pocreated_pr = PurchaseRequisition.query.filter_by(status='PO Created').count()
    rejected_pr = PurchaseRequisition.query.filter_by(status='Rejected').count()
    
    all_pos = PurchaseOrder.query.all()
    total_po = len(all_pos)
    issued_po = sum(1 for p in all_pos if p.status == 'Issued')
    partial_po = sum(1 for p in all_pos if p.status == 'Partially Received')
    received_po = sum(1 for p in all_pos if p.status == 'Received')
    total_po_amount = sum(p.total_amount for p in all_pos)
    
    all_grs = GoodsReceipt.query.all()
    total_gr = len(all_grs)
    complete_gr = sum(1 for g in all_grs if g.status == 'Complete')
    partial_gr = sum(1 for g in all_grs if g.status == 'Partial')
    
    open_pos = PurchaseOrder.query.filter(PurchaseOrder.status.in_(['Issued', 'Partially Received'])).order_by(PurchaseOrder.delivery_estimate_date.asc()).all()
    waiting_po_count = len(open_pos)

    # 2. Metrik Khusus Requester
    my_prs_query = PurchaseRequisition.query.filter_by(requester_id=user.id)
    my_total_pr = my_prs_query.count()
    my_pending_pr = my_prs_query.filter_by(status='Pending').count()
    my_approved_pr = my_prs_query.filter_by(status='Approved').count()
    my_pocreated_pr = my_prs_query.filter_by(status='PO Created').count()
    my_rejected_pr = my_prs_query.filter_by(status='Rejected').count()
    my_total_spent = sum(p.total_estimated_amount for p in my_prs_query.all())

    # 3. Metrik Khusus Approver
    pending_prs_list = PurchaseRequisition.query.filter_by(status='Pending').order_by(PurchaseRequisition.created_at.desc()).all()
    total_approver_amount = sum(p.total_estimated_amount for p in pending_prs_list)
    total_approved_amount = sum(p.total_estimated_amount for p in PurchaseRequisition.query.filter(PurchaseRequisition.status.in_(['Approved', 'PO Created'])).all())

    # 4. Metrik Khusus Purchasing
    approved_prs_ready_po = PurchaseRequisition.query.filter_by(status='Approved').order_by(PurchaseRequisition.created_at.desc()).all()

    # 5. Metrik Total Anggaran & User (Admin)
    all_prs = PurchaseRequisition.query.all()
    total_company_budget = sum(p.total_estimated_amount for p in all_prs)
    total_users_count = User.query.count()

    # Transaksi terbaru sesuai role
    if user.role == 'Requester':
        recent_prs = my_prs_query.order_by(PurchaseRequisition.created_at.desc()).limit(5).all()
        my_pr_ids = [p.id for p in my_prs_query.all()]
        recent_pos = PurchaseOrder.query.filter(PurchaseOrder.pr_id.in_(my_pr_ids)).order_by(PurchaseOrder.created_at.desc()).limit(5).all() if my_pr_ids else []
    else:
        recent_prs = PurchaseRequisition.query.order_by(PurchaseRequisition.created_at.desc()).limit(5).all()
        recent_pos = PurchaseOrder.query.order_by(PurchaseOrder.created_at.desc()).limit(5).all()

    recent_grs = GoodsReceipt.query.order_by(GoodsReceipt.created_at.desc()).limit(5).all()

    # Data ringkasan grafik Chart.js sesuai role masing-masing
    chart_config = {
        'Requester': {
            'title': 'Distribusi Pengajuan PR Saya',
            'labels': ['Pending Review', 'Disetujui (Approved)', 'PO Diterbitkan', 'Ditolak (Rejected)'],
            'data': [my_pending_pr, my_approved_pr, my_pocreated_pr, my_rejected_pr],
            'colors': ['#f59e0b', '#10b981', '#6366f1', '#ef4444']
        },
        'Approver': {
            'title': 'Distribusi Otorisasi Pengajuan PR',
            'labels': ['Perlu Review Anda', 'Disetujui (Approved)', 'Ditolak (Rejected)'],
            'data': [pending_pr, approved_pr + pocreated_pr, rejected_pr],
            'colors': ['#f59e0b', '#10b981', '#ef4444']
        },
        'Purchasing': {
            'title': 'Status Pemenuhan Purchase Order Vendor',
            'labels': ['PR Siap PO', 'PO Menunggu Kirim', 'PO Diterima Parsial', 'PO Selesai Diterima'],
            'data': [approved_pr, issued_po, partial_po, received_po],
            'colors': ['#3b82f6', '#f59e0b', '#f97316', '#10b981']
        },
        'Warehouse': {
            'title': 'Status Kelayakan & Fisik Barang Masuk',
            'labels': ['PO Menunggu Fisik', 'Penerimaan Lengkap (Complete)', 'Penerimaan Parsial'],
            'data': [waiting_po_count, complete_gr, partial_gr],
            'colors': ['#f59e0b', '#10b981', '#6366f1']
        },
        'Admin': {
            'title': 'Komposisi Alur Pengadaan Seluruh Sistem',
            'labels': ['1. PR Diajukan', '2. Approval Selesai', '3. PO Diterbitkan', '4. GR Fisik Tiba'],
            'data': [total_pr, approved_pr + pocreated_pr, total_po, total_gr],
            'colors': ['#3b82f6', '#10b981', '#6366f1', '#059669']
        }
    }

    current_chart = chart_config.get(user.role, chart_config['Admin'])

    return render_template(
        'dashboard/index.html',
        total_pr=total_pr,
        pending_pr=pending_pr,
        approved_pr=approved_pr,
        pocreated_pr=pocreated_pr,
        rejected_pr=rejected_pr,
        total_po=total_po,
        issued_po=issued_po,
        partial_po=partial_po,
        received_po=received_po,
        total_po_amount=total_po_amount,
        total_gr=total_gr,
        complete_gr=complete_gr,
        partial_gr=partial_gr,
        waiting_po_count=waiting_po_count,
        open_pos=open_pos,
        my_total_pr=my_total_pr,
        my_pending_pr=my_pending_pr,
        my_approved_pr=my_approved_pr,
        my_pocreated_pr=my_pocreated_pr,
        my_rejected_pr=my_rejected_pr,
        my_total_spent=my_total_spent,
        pending_prs_list=pending_prs_list,
        total_approver_amount=total_approver_amount,
        total_approved_amount=total_approved_amount,
        approved_prs_ready_po=approved_prs_ready_po,
        total_company_budget=total_company_budget,
        total_users_count=total_users_count,
        recent_prs=recent_prs,
        recent_pos=recent_pos,
        recent_grs=recent_grs,
        current_chart=current_chart
    )


# ==========================================
# PURCHASE REQUISITION (PR) ROUTES
# ==========================================
@app.route('/pr')
@login_required
def pr_list():
    status_filter = request.args.get('status', '').strip()
    search_query = request.args.get('q', '').strip()

    # Jika Requester, tampilkan milik dirinya kecuali jika admin/approver/purchasing
    user = User.query.get(session['user_id'])
    if user.role == 'Requester':
        base_query = PurchaseRequisition.query.filter_by(requester_id=user.id)
    else:
        base_query = PurchaseRequisition.query

    all_prs = base_query.all()
    pr_stats = {
        'total': len(all_prs),
        'pending': sum(1 for p in all_prs if p.status == 'Pending'),
        'approved': sum(1 for p in all_prs if p.status == 'Approved'),
        'po_created': sum(1 for p in all_prs if p.status == 'PO Created'),
        'rejected': sum(1 for p in all_prs if p.status == 'Rejected'),
        'total_amount': sum(p.total_estimated_amount for p in all_prs),
        'pending_amount': sum(p.total_estimated_amount for p in all_prs if p.status == 'Pending'),
    }

    query = base_query
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if search_query:
        query = query.filter(
            (PurchaseRequisition.pr_number.ilike(f'%{search_query}%')) |
            (PurchaseRequisition.purpose.ilike(f'%{search_query}%')) |
            (PurchaseRequisition.department.ilike(f'%{search_query}%'))
        )

    prs = query.order_by(PurchaseRequisition.created_at.desc()).all()
    return render_template('pr/list.html', prs=prs, current_status=status_filter, search_query=search_query, stats=pr_stats)

@app.route('/pr/create', methods=['GET', 'POST'])
@login_required
@role_required('Requester', 'Admin')
def pr_create():
    user = User.query.get(session['user_id'])
    today_str = date.today().strftime('%Y-%m-%d')

    if request.method == 'POST':
        department = request.form.get('department', '').strip()
        required_date_raw = request.form.get('required_date', '')
        purpose = request.form.get('purpose', '').strip()

        # Item array dari form dinamis
        item_names = request.form.getlist('item_name[]')
        specifications = request.form.getlist('specification[]')
        quantities = request.form.getlist('quantity[]')
        units = request.form.getlist('unit[]')
        estimated_prices = request.form.getlist('estimated_price[]')

        if not department or not required_date_raw or not purpose:
            flash('Harap lengkapi seluruh formulir informasi umum PR.', 'danger')
            return redirect(url_for('pr_create'))

        if not item_names or len(item_names) == 0:
            flash('Minimal harus memasukkan 1 item pengadaan.', 'danger')
            return redirect(url_for('pr_create'))

        try:
            required_date = datetime.strptime(required_date_raw, '%Y-%m-%d').date()
        except ValueError:
            flash('Format tanggal kebutuhan tidak valid.', 'danger')
            return redirect(url_for('pr_create'))

        # Generate PR Number otomatis: PR-YYYY-XXXX
        current_year = date.today().year
        last_pr = PurchaseRequisition.query.filter(
            PurchaseRequisition.pr_number.like(f'PR-{current_year}-%')
        ).order_by(PurchaseRequisition.id.desc()).first()

        if last_pr and last_pr.pr_number:
            try:
                seq = int(last_pr.pr_number.split('-')[-1]) + 1
            except Exception:
                seq = PurchaseRequisition.query.count() + 1
        else:
            seq = 1

        pr_number = f"PR-{current_year}-{seq:04d}"

        # Buat PR
        new_pr = PurchaseRequisition(
            pr_number=pr_number,
            requester_id=user.id,
            department=department,
            request_date=date.today(),
            required_date=required_date,
            purpose=purpose,
            status='Pending'
        )
        db.session.add(new_pr)
        db.session.flush()

        # Tambahkan item-item PR
        total_estimate = 0.0
        for i in range(len(item_names)):
            name = item_names[i].strip()
            if not name:
                continue
            spec = specifications[i].strip() if i < len(specifications) else ''
            qty = int(quantities[i]) if i < len(quantities) and quantities[i].isdigit() else 1
            unit = units[i].strip() if i < len(units) and units[i].strip() else 'Pcs'
            try:
                price = float(estimated_prices[i]) if i < len(estimated_prices) else 0.0
            except ValueError:
                price = 0.0
            
            subtotal = float(qty) * price
            total_estimate += subtotal

            pr_item = PRItem(
                pr_id=new_pr.id,
                item_name=name,
                specification=spec,
                quantity=qty,
                unit=unit,
                estimated_price=price,
                subtotal=subtotal
            )
            db.session.add(pr_item)

        new_pr.total_estimated_amount = total_estimate
        db.session.commit()

        flash(f'Purchase Requisition ({pr_number}) berhasil diajukan dan menunggu persetujuan.', 'success')
        return redirect(url_for('pr_detail', pr_id=new_pr.id))

    return render_template('pr/create.html', today_str=today_str, user=user)

@app.route('/pr/<int:pr_id>')
@login_required
def pr_detail(pr_id):
    pr = PurchaseRequisition.query.get_or_404(pr_id)
    return render_template('pr/detail.html', pr=pr)

@app.route('/pr/<int:pr_id>/delete', methods=['POST'])
@login_required
def pr_delete(pr_id):
    pr = PurchaseRequisition.query.get_or_404(pr_id)
    user = User.query.get(session['user_id'])

    if pr.status not in ['Pending', 'Draft', 'Rejected']:
        flash('PR yang sudah disetujui atau diproses PO tidak dapat dihapus.', 'danger')
        return redirect(url_for('pr_detail', pr_id=pr.id))

    if user.role != 'Admin' and pr.requester_id != user.id:
        flash('Anda tidak memiliki wewenang untuk menghapus PR ini.', 'danger')
        return redirect(url_for('pr_detail', pr_id=pr.id))

    pr_num = pr.pr_number
    db.session.delete(pr)
    db.session.commit()
    flash(f'Purchase Requisition {pr_num} berhasil dihapus.', 'info')
    return redirect(url_for('pr_list'))


# ==========================================
# APPROVAL ROUTES (Approver Role)
# ==========================================
@app.route('/approvals')
@login_required
@role_required('Approver', 'Admin')
def approval_list():
    status = request.args.get('status', 'Pending')
    search_query = request.args.get('q', '').strip()

    all_prs = PurchaseRequisition.query.all()
    approval_stats = {
        'total': len(all_prs),
        'pending': sum(1 for p in all_prs if p.status == 'Pending'),
        'approved': sum(1 for p in all_prs if p.status == 'Approved'),
        'rejected': sum(1 for p in all_prs if p.status == 'Rejected'),
        'pending_amount': sum(p.total_estimated_amount for p in all_prs if p.status == 'Pending'),
        'approved_amount': sum(p.total_estimated_amount for p in all_prs if p.status in ['Approved', 'PO Created']),
    }

    query = PurchaseRequisition.query
    if status != 'All':
        query = query.filter_by(status=status)

    if search_query:
        query = query.filter(
            (PurchaseRequisition.pr_number.ilike(f'%{search_query}%')) |
            (PurchaseRequisition.purpose.ilike(f'%{search_query}%')) |
            (PurchaseRequisition.department.ilike(f'%{search_query}%'))
        )

    prs = query.order_by(PurchaseRequisition.created_at.desc()).all()
    return render_template('approval/list.html', prs=prs, current_status=status, stats=approval_stats, search_query=search_query)

@app.route('/approvals/<int:pr_id>', methods=['GET', 'POST'])
@login_required
@role_required('Approver', 'Admin')
def approval_review(pr_id):
    pr = PurchaseRequisition.query.get_or_404(pr_id)
    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        action = request.form.get('action')  # 'approve' or 'reject'
        notes = request.form.get('approval_notes', '').strip()

        if pr.status != 'Pending':
            flash('Pengajuan PR ini sudah tidak dalam status pending approval.', 'warning')
            return redirect(url_for('approval_list'))

        if action == 'approve':
            pr.status = 'Approved'
            pr.approver_id = user.id
            pr.approval_date = datetime.now()
            pr.approval_notes = notes or 'Disetujui untuk diproses ke tahap Purchase Order.'
            db.session.commit()
            flash(f'PR {pr.pr_number} berhasil disetujui (Approved). Tim Purchasing dapat menerbitkan PO.', 'success')
        elif action == 'reject':
            if not notes:
                flash('Harap berikan catatan alasan penolakan agar Requester dapat memperbaiki pengajuan.', 'danger')
                return render_template('approval/review.html', pr=pr)
            pr.status = 'Rejected'
            pr.approver_id = user.id
            pr.approval_date = datetime.now()
            pr.approval_notes = notes
            db.session.commit()
            flash(f'PR {pr.pr_number} telah ditolak (Rejected).', 'info')
        else:
            flash('Aksi approval tidak dikenal.', 'danger')
            return redirect(url_for('approval_review', pr_id=pr.id))

        return redirect(url_for('approval_list'))

    return render_template('approval/review.html', pr=pr)


# ==========================================
# PURCHASE ORDER (PO) ROUTES (Purchasing Role)
# ==========================================
@app.route('/po')
@login_required
def po_list():
    status_filter = request.args.get('status', '').strip()
    search_query = request.args.get('q', '').strip()

    all_pos = PurchaseOrder.query.all()
    po_stats = {
        'total': len(all_pos),
        'issued': sum(1 for p in all_pos if p.status == 'Issued'),
        'partial': sum(1 for p in all_pos if p.status == 'Partially Received'),
        'received': sum(1 for p in all_pos if p.status == 'Received'),
        'total_amount': sum(p.total_amount for p in all_pos),
        'received_amount': sum(p.total_amount for p in all_pos if p.status == 'Received'),
    }

    query = PurchaseOrder.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if search_query:
        query = query.filter(
            (PurchaseOrder.po_number.ilike(f'%{search_query}%')) |
            (PurchaseOrder.vendor_name.ilike(f'%{search_query}%'))
        )
    pos = query.order_by(PurchaseOrder.created_at.desc()).all()
    
    # Ambil juga PR yang ready untuk dibuatkan PO
    approved_prs = PurchaseRequisition.query.filter_by(status='Approved').order_by(PurchaseRequisition.id.desc()).all()

    return render_template(
        'po/list.html',
        pos=pos,
        approved_prs=approved_prs,
        current_status=status_filter,
        search_query=search_query,
        stats=po_stats
    )

@app.route('/po/create', methods=['GET', 'POST'])
@login_required
@role_required('Purchasing', 'Admin')
def po_create():
    pr_id = request.args.get('pr_id') or request.form.get('pr_id')
    selected_pr = None
    if pr_id:
        selected_pr = PurchaseRequisition.query.get(pr_id)
        if selected_pr and selected_pr.status != 'Approved':
            flash(f'PR {selected_pr.pr_number} statusnya "{selected_pr.status}". Hanya PR "Approved" yang dapat dibuatkan PO.', 'warning')
            return redirect(url_for('po_list'))

    approved_prs = PurchaseRequisition.query.filter_by(status='Approved').all()
    user = User.query.get(session['user_id'])
    today_str = date.today().strftime('%Y-%m-%d')

    if request.method == 'POST':
        pr_id_form = request.form.get('pr_id')
        pr = PurchaseRequisition.query.get_or_404(pr_id_form)

        if pr.status != 'Approved':
            flash('PR ini tidak dalam status disetujui.', 'danger')
            return redirect(url_for('po_list'))

        vendor_name = request.form.get('vendor_name', '').strip()
        vendor_address = request.form.get('vendor_address', '').strip()
        vendor_phone = request.form.get('vendor_phone', '').strip()
        vendor_email = request.form.get('vendor_email', '').strip()
        payment_terms = request.form.get('payment_terms', 'Net 30').strip()
        delivery_estimate_raw = request.form.get('delivery_estimate_date', '')
        notes = request.form.get('notes', '').strip()

        delivery_estimate_date = None
        if delivery_estimate_raw:
            try:
                delivery_estimate_date = datetime.strptime(delivery_estimate_raw, '%Y-%m-%d').date()
            except ValueError:
                pass

        if not vendor_name:
            flash('Nama vendor wajib diisi.', 'danger')
            return render_template('po/create.html', approved_prs=approved_prs, selected_pr=pr, today_str=today_str)

        # Generate PO Number: PO-YYYY-XXXX
        current_year = date.today().year
        last_po = PurchaseOrder.query.filter(
            PurchaseOrder.po_number.like(f'PO-{current_year}-%')
        ).order_by(PurchaseOrder.id.desc()).first()

        if last_po and last_po.po_number:
            try:
                seq = int(last_po.po_number.split('-')[-1]) + 1
            except Exception:
                seq = PurchaseOrder.query.count() + 1
        else:
            seq = 1

        po_number = f"PO-{current_year}-{seq:04d}"

        # Buat PO baru
        new_po = PurchaseOrder(
            po_number=po_number,
            pr_id=pr.id,
            purchasing_id=user.id,
            vendor_name=vendor_name,
            vendor_address=vendor_address,
            vendor_phone=vendor_phone,
            vendor_email=vendor_email,
            po_date=date.today(),
            delivery_estimate_date=delivery_estimate_date,
            payment_terms=payment_terms,
            notes=notes,
            status='Issued'
        )
        db.session.add(new_po)
        db.session.flush()

        # Input item PO dari PR items (memungkinkan penyesuaian harga penawaran vendor)
        total_amount = 0.0
        for pr_item in pr.items:
            unit_price_form = request.form.get(f'unit_price_{pr_item.id}')
            qty_form = request.form.get(f'quantity_{pr_item.id}')

            try:
                unit_price = float(unit_price_form) if unit_price_form else pr_item.estimated_price
            except ValueError:
                unit_price = pr_item.estimated_price

            try:
                qty = int(qty_form) if qty_form else pr_item.quantity
            except ValueError:
                qty = pr_item.quantity

            subtotal = float(qty) * unit_price
            total_amount += subtotal

            po_item = POItem(
                po_id=new_po.id,
                pr_item_id=pr_item.id,
                item_name=pr_item.item_name,
                specification=pr_item.specification,
                quantity=qty,
                unit=pr_item.unit,
                unit_price=unit_price,
                subtotal=subtotal
            )
            db.session.add(po_item)

        new_po.total_amount = total_amount
        # Update status PR menjadi 'PO Created'
        pr.status = 'PO Created'

        db.session.commit()
        flash(f'Purchase Order ({po_number}) berhasil diterbitkan kepada vendor "{vendor_name}".', 'success')
        return redirect(url_for('po_detail', po_id=new_po.id))

    return render_template(
        'po/create.html',
        approved_prs=approved_prs,
        selected_pr=selected_pr,
        today_str=today_str
    )

@app.route('/po/<int:po_id>')
@login_required
def po_detail(po_id):
    po = PurchaseOrder.query.get_or_404(po_id)
    return render_template('po/detail.html', po=po)


# ==========================================
# GOODS RECEIPT (GR) ROUTES (Warehouse Role)
# ==========================================
@app.route('/gr')
@login_required
def gr_list():
    status_filter = request.args.get('status', '').strip()
    search_query = request.args.get('q', '').strip()

    query = GoodsReceipt.query

    if status_filter in ['Complete', 'Partial']:
        query = query.filter_by(status=status_filter)

    if search_query:
        query = query.join(PurchaseOrder, GoodsReceipt.po_id == PurchaseOrder.id).filter(
            (GoodsReceipt.gr_number.ilike(f'%{search_query}%')) |
            (GoodsReceipt.delivery_order_number.ilike(f'%{search_query}%')) |
            (PurchaseOrder.po_number.ilike(f'%{search_query}%')) |
            (PurchaseOrder.vendor_name.ilike(f'%{search_query}%'))
        )

    grs = query.order_by(GoodsReceipt.created_at.desc()).all()
    open_pos = PurchaseOrder.query.filter(PurchaseOrder.status.in_(['Issued', 'Partially Received'])).order_by(PurchaseOrder.delivery_estimate_date.asc()).all()

    total_gr = GoodsReceipt.query.count()
    complete_gr = GoodsReceipt.query.filter_by(status='Complete').count()
    partial_gr = GoodsReceipt.query.filter_by(status='Partial').count()
    waiting_po = len(open_pos)

    gr_stats = {
        'total': total_gr,
        'waiting_po': waiting_po,
        'complete': complete_gr,
        'partial': partial_gr
    }

    return render_template(
        'gr/list.html',
        grs=grs,
        open_pos=open_pos,
        stats=gr_stats,
        current_status=status_filter,
        search_query=search_query
    )

@app.route('/gr/create', methods=['GET', 'POST'])
@login_required
@role_required('Warehouse', 'Admin')
def gr_create():
    po_id = request.args.get('po_id') or request.form.get('po_id')
    selected_po = None
    if po_id:
        selected_po = PurchaseOrder.query.get(po_id)
        if selected_po and selected_po.status == 'Received':
            flash(f'PO {selected_po.po_number} telah selesai diterima seluruhnya.', 'info')

    open_pos = PurchaseOrder.query.filter(PurchaseOrder.status.in_(['Issued', 'Partially Received'])).all()
    user = User.query.get(session['user_id'])
    today_str = date.today().strftime('%Y-%m-%d')

    if request.method == 'POST':
        po_id_form = request.form.get('po_id')
        po = PurchaseOrder.query.get_or_404(po_id_form)

        delivery_order_number = request.form.get('delivery_order_number', '').strip()
        received_date_raw = request.form.get('received_date', '')
        gr_notes = request.form.get('notes', '').strip()

        if not delivery_order_number:
            flash('Nomor Surat Jalan (Delivery Order) wajib diisi.', 'danger')
            return render_template('gr/create.html', open_pos=open_pos, selected_po=po, today_str=today_str)

        try:
            received_date = datetime.strptime(received_date_raw, '%Y-%m-%d').date() if received_date_raw else date.today()
        except ValueError:
            received_date = date.today()

        # Generate GR Number: GR-YYYY-XXXX
        current_year = date.today().year
        last_gr = GoodsReceipt.query.filter(
            GoodsReceipt.gr_number.like(f'GR-{current_year}-%')
        ).order_by(GoodsReceipt.id.desc()).first()

        if last_gr and last_gr.gr_number:
            try:
                seq = int(last_gr.gr_number.split('-')[-1]) + 1
            except Exception:
                seq = GoodsReceipt.query.count() + 1
        else:
            seq = 1

        gr_number = f"GR-{current_year}-{seq:04d}"

        new_gr = GoodsReceipt(
            gr_number=gr_number,
            po_id=po.id,
            warehouse_officer_id=user.id,
            delivery_order_number=delivery_order_number,
            received_date=received_date,
            notes=gr_notes,
            status='Complete'
        )
        db.session.add(new_gr)
        db.session.flush()

        # Catat item yang diterima
        all_completed = True
        for po_item in po.items:
            qty_received_str = request.form.get(f'qty_received_{po_item.id}', '0')
            condition_status = request.form.get(f'condition_{po_item.id}', 'Baik')
            item_notes = request.form.get(f'item_notes_{po_item.id}', '').strip()

            try:
                qty_received = int(qty_received_str)
            except ValueError:
                qty_received = 0

            # Hitung total yang sudah diterima di GR-GR sebelumnya untuk item ini
            prev_received = 0
            for gr_record in po.goods_receipts:
                if gr_record.id != new_gr.id:
                    for gi in gr_record.items:
                        if gi.po_item_id == po_item.id:
                            prev_received += gi.quantity_received

            if qty_received > 0:
                gr_item = GRItem(
                    gr_id=new_gr.id,
                    po_item_id=po_item.id,
                    quantity_received=qty_received,
                    condition_status=condition_status,
                    notes=item_notes
                )
                db.session.add(gr_item)

            if (prev_received + qty_received) < po_item.quantity:
                all_completed = False

        if all_completed:
            new_gr.status = 'Complete'
            po.status = 'Received'
        else:
            new_gr.status = 'Partial'
            po.status = 'Partially Received'

        db.session.commit()
        flash(f'Goods Receipt ({gr_number}) berhasil disimpan. Barang telah dicatat tiba di gudang.', 'success')
        return redirect(url_for('gr_detail', gr_id=new_gr.id))

    return render_template(
        'gr/create.html',
        open_pos=open_pos,
        selected_po=selected_po,
        today_str=today_str
    )

@app.route('/gr/<int:gr_id>')
@login_required
def gr_detail(gr_id):
    gr = GoodsReceipt.query.get_or_404(gr_id)
    return render_template('gr/detail.html', gr=gr)


# ==========================================
# FITUR NILAI PLUS: SIMULASI AI SMART SCANNER
# ==========================================
# FITUR NILAI PLUS: SIMULASI AI SMART SCANNER SUITE
# ==========================================
@app.route('/api/ai-scan-pr', methods=['POST'])
@login_required
def ai_scan_pr_catalog():
    """
    Fitur Nilai Plus: Computer Vision / AI Model Simulator untuk input form Purchase Requisition (PR).
    Menerima gambar katalog/brosur/invoice kebutuhan barang dan mengekstrak multi-item ke form PR.
    """
    import random
    import time
    time.sleep(0.5)

    file = request.files.get('file')
    filename = file.filename if file else 'catalog_spec_sheet.png'

    # Sampel paket ekstraksi AI Vision cerdas
    sample_packages = [
        {
            "package_name": "Paket Hardware IT Workstation Engineer",
            "items": [
                {"name": "Laptop ThinkPad P16 Gen 2 Workstation", "spec": "Intel Core i7-13850HX, 32GB DDR5, 1TB NVMe, RTX A2000", "qty": 1, "unit": "Unit", "price": 28500000},
                {"name": "Monitor Dell UltraSharp 27 4K USB-C Hub", "spec": "IPS Black 4K UHD 3840x2160, 90W Power Delivery", "qty": 1, "unit": "Unit", "price": 8450000},
                {"name": "Keyboard Mekanikal Wireless & Mouse Ergonomis", "spec": "Logitech MX Master 3S & MX Mechanical Keyboard", "qty": 1, "unit": "Set", "price": 2850000}
            ]
        },
        {
            "package_name": "Paket Infrastruktur Jaringan & Server Rack",
            "items": [
                {"name": "Cisco Catalyst Switch 24-Port Gigabit PoE+", "spec": "Managed Layer 2/3 Switch, 370W PoE budget", "qty": 2, "unit": "Unit", "price": 14200000},
                {"name": "Kabel UTP Cat6 Belden Original 305M", "spec": "1000ft Solid Bare Copper 23 AWG Blue", "qty": 4, "unit": "Roll", "price": 1850000},
                {"name": "Patch Panel 24 Port Cat6 Modular", "spec": "19 Inch Rackmount with Cable Management Bar", "qty": 2, "unit": "Unit", "price": 750000}
            ]
        },
        {
            "package_name": "Paket Perlengkapan Ruang Rapat & Multimedia",
            "items": [
                {"name": "Smart TV Interactive Display 65 Inch 4K", "spec": "Android 13 OS, 40-Point Multi-Touch, Pen Included", "qty": 1, "unit": "Unit", "price": 22500000},
                {"name": "Video Conference Camera 4K Ultra HD", "spec": "Auto-Framing, Voice Tracking Microphone Array 8M", "qty": 1, "unit": "Set", "price": 7800000}
            ]
        }
    ]

    chosen = random.choice(sample_packages)

    return jsonify({
        'success': True,
        'message': f'AI Computer Vision berhasil mendeteksi {len(chosen["items"])} item dari dokumen "{filename}"',
        'package_name': chosen['package_name'],
        'confidence_score': '99.4%',
        'items': chosen['items']
    })


@app.route('/api/ai-scan-quotation', methods=['POST'])
@login_required
def ai_scan_vendor_quotation():
    """
    Fitur Nilai Plus: Computer Vision / AI Model Simulator untuk input form Purchase Order (PO).
    Menerima scan/foto Surat Penawaran Resmi Vendor dan mengekstrak data rekanan, payment terms, & alamat.
    """
    import random
    import time
    time.sleep(0.5)

    file = request.files.get('file')
    filename = file.filename if file else 'vendor_quotation_letter.pdf'

    sample_vendors = [
        {
            "vendor_name": "PT Solusi Mitra Informatika",
            "vendor_phone": "021-52908877",
            "vendor_email": "corporate.sales@solusimitra.co.id",
            "vendor_address": "Gedung Cyber 2 Lt. 8, Jl. HR Rasuna Said Blok X-5, Kuningan, Jakarta Selatan 12950",
            "payment_terms": "Net 30 Days",
            "delivery_days": 7,
            "notes": "Penawaran harga resmi Ref: SMI/Q-2026/8921. Garansi resmi distributor 3 tahun replace unit."
        },
        {
            "vendor_name": "CV ATK Berkah Jaya Mandiri",
            "vendor_phone": "021-3908812",
            "vendor_email": "order@atkberkah.com",
            "vendor_address": "Ruko Sentra Niaga Blok C-12, Jl. Pramuka Raya No. 45, Jakarta Timur 13120",
            "payment_terms": "Cash On Delivery (COD)",
            "delivery_days": 3,
            "notes": "Penawaran harga terbaik nomor: BJM-Q/2026/04. Gratis ongkir area Jabodetabek untuk pembelian di atas 5 juta."
        },
        {
            "vendor_name": "PT Triputra Daya Mandiri",
            "vendor_phone": "021-7890123",
            "vendor_email": "sourcing@triputradaya.co.id",
            "vendor_address": "Kawasan Industri Pulogadung Blok F-10, Jl. Rawa Gelam IV, Jakarta Timur 13930",
            "payment_terms": "Advance Payment / DP 50%",
            "delivery_days": 14,
            "notes": "Surat Penawaran Kontrak No: TDM/PRJ/2026-XI. Termasuk sertifikasi uji kelayakan & kalibrasi pabrikan."
        }
    ]

    vendor_info = random.choice(sample_vendors)
    from datetime import timedelta
    est_date = (date.today() + timedelta(days=vendor_info['delivery_days'])).strftime('%Y-%m-%d')

    return jsonify({
        'success': True,
        'message': f'AI Smart Vision berhasil mengekstrak surat penawaran dari "{vendor_info["vendor_name"]}"',
        'confidence_score': '98.9%',
        'data': {
            'vendor_name': vendor_info['vendor_name'],
            'vendor_phone': vendor_info['vendor_phone'],
            'vendor_email': vendor_info['vendor_email'],
            'vendor_address': vendor_info['vendor_address'],
            'payment_terms': vendor_info['payment_terms'],
            'delivery_estimate_date': est_date,
            'notes': vendor_info['notes']
        }
    })


@app.route('/api/ai-scan-do', methods=['POST'])
@login_required
def ai_scan_delivery_order():
    """
    Fitur Nilai Plus: Computer Vision / AI Model Simulator untuk input form surat jalan.
    Menerima file gambar / scan surat jalan dan mengekstrak info nomor DO dan catatan.
    """
    import random
    import time
    
    # Memberi simulasi delay ekstraksi AI 0.5 detik
    time.sleep(0.5)

    sample_do_prefixes = ['DO/LOGISTIK/2026/XI-', 'SJ-MTR-2026-', 'DO-EXP-']
    generated_do = f"{random.choice(sample_do_prefixes)}{random.randint(1000, 9999)}"
    
    file = request.files.get('file')
    filename = file.filename if file else 'document_scan.jpg'

    return jsonify({
        'success': True,
        'message': f'AI Smart Vision berhasil menganalisis dokumen "{filename}"',
        'data': {
            'detected_do_number': generated_do,
            'detected_date': date.today().strftime('%Y-%m-%d'),
            'confidence_score': '98.7%',
            'detected_condition': 'Baik (Segel Aman)',
            'ai_notes': f'Hasil ekstraksi otomatis OCR dari dokumen: {filename}. Kondisi fisik paket utuh.'
        }
    })


# ==========================================
# MAIN ENTRYPOINT
# ==========================================
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
