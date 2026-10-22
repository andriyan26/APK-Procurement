/**
 * Aplikasi Procurement Enterprise
 * Interaksi Dynamic Form, Kalkulasi Real-time, dan Integrasi AI Scanner
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Tooltips Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 2. Format Mata Uang IDR Helper
    function formatIDR(number) {
        return new Intl.NumberFormat('id-ID', {
            style: 'currency',
            currency: 'IDR',
            maximumFractionDigits: 0
        }).format(number);
    }

    // ==========================================
    // FORM DINAMIS PURCHASE REQUISITION (PR)
    // ==========================================
    const prItemsTable = document.getElementById('pr-items-tbody');
    const btnAddItem = document.getElementById('btn-add-item');
    const grandTotalElement = document.getElementById('pr-grand-total');

    function calculatePRTotals() {
        if (!prItemsTable) return;
        let grandTotal = 0;
        const rows = prItemsTable.querySelectorAll('tr.item-row');
        rows.forEach(row => {
            const qtyInput = row.querySelector('.item-qty');
            const priceInput = row.querySelector('.item-price');
            const subtotalText = row.querySelector('.item-subtotal-text');

            const qty = parseFloat(qtyInput ? qtyInput.value : 0) || 0;
            const price = parseFloat(priceInput ? priceInput.value : 0) || 0;
            const subtotal = qty * price;
            grandTotal += subtotal;

            if (subtotalText) {
                subtotalText.textContent = formatIDR(subtotal);
            }
        });

        if (grandTotalElement) {
            grandTotalElement.textContent = formatIDR(grandTotal);
        }
    }

    if (prItemsTable) {
        // Event listener saat input qty atau harga berubah
        prItemsTable.addEventListener('input', function (e) {
            if (e.target.classList.contains('item-qty') || e.target.classList.contains('item-price')) {
                calculatePRTotals();
            }
        });

        // Event listener untuk menghapus baris
        prItemsTable.addEventListener('click', function (e) {
            const btnRemove = e.target.closest('.btn-remove-item');
            if (btnRemove) {
                const rows = prItemsTable.querySelectorAll('tr.item-row');
                if (rows.length > 1) {
                    btnRemove.closest('tr').remove();
                    renumberRows();
                    calculatePRTotals();
                } else {
                    alert('Minimal harus ada 1 baris item pengadaan.');
                }
            }
        });

        function renumberRows() {
            const rows = prItemsTable.querySelectorAll('tr.item-row');
            rows.forEach((row, index) => {
                const numCol = row.querySelector('.row-number');
                if (numCol) numCol.textContent = index + 1;
            });
        }

        // Tambah baris item baru
        if (btnAddItem) {
            btnAddItem.addEventListener('click', function () {
                const rowCount = prItemsTable.querySelectorAll('tr.item-row').length + 1;
                const newRow = document.createElement('tr');
                newRow.className = 'item-row';
                newRow.innerHTML = `
                    <td class="text-center row-number fw-bold text-muted">${rowCount}</td>
                    <td>
                        <input type="text" name="item_name[]" class="form-control form-control-sm" placeholder="Contoh: Laptop Dell Latitude" required>
                    </td>
                    <td>
                        <input type="text" name="specification[]" class="form-control form-control-sm" placeholder="Spesifikasi detail & tipe">
                    </td>
                    <td style="width: 110px;">
                        <input type="number" name="quantity[]" class="form-control form-control-sm text-center item-qty" value="1" min="1" required>
                    </td>
                    <td style="width: 120px;">
                        <select name="unit[]" class="form-select form-select-sm">
                            <option value="Unit" selected>Unit</option>
                            <option value="Pcs">Pcs</option>
                            <option value="Box">Box</option>
                            <option value="Rim">Rim</option>
                            <option value="Set">Set</option>
                            <option value="Roll">Roll</option>
                            <option value="Pack">Pack</option>
                            <option value="Meter">Meter</option>
                        </select>
                    </td>
                    <td style="width: 180px;">
                        <div class="input-group input-group-sm">
                            <span class="input-group-text">Rp</span>
                            <input type="number" name="estimated_price[]" class="form-control item-price" value="0" min="0" step="1000" required>
                        </div>
                    </td>
                    <td class="text-end fw-bold text-primary item-subtotal-text" style="width: 170px;">
                        Rp 0
                    </td>
                    <td class="text-center" style="width: 60px;">
                        <button type="button" class="btn btn-outline-danger btn-sm btn-remove-item" title="Hapus Item">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                `;
                prItemsTable.appendChild(newRow);
                calculatePRTotals();
            });
        }

        // Inisialisasi awal
        calculatePRTotals();
    }

    // ==========================================
    // FORM PURCHASE ORDER (PO) CALCULATIONS
    // ==========================================
    const poItemsTable = document.getElementById('po-items-tbody');
    const poGrandTotalElement = document.getElementById('po-grand-total');

    function calculatePOTotals() {
        if (!poItemsTable) return;
        let grandTotal = 0;
        const rows = poItemsTable.querySelectorAll('tr.po-item-row');
        rows.forEach(row => {
            const qtyInput = row.querySelector('.po-item-qty');
            const priceInput = row.querySelector('.po-item-price');
            const subtotalText = row.querySelector('.po-item-subtotal-text');

            const qty = parseFloat(qtyInput ? qtyInput.value : 0) || 0;
            const price = parseFloat(priceInput ? priceInput.value : 0) || 0;
            const subtotal = qty * price;
            grandTotal += subtotal;

            if (subtotalText) {
                subtotalText.textContent = formatIDR(subtotal);
            }
        });

        if (poGrandTotalElement) {
            poGrandTotalElement.textContent = formatIDR(grandTotal);
        }
    }

    if (poItemsTable) {
        poItemsTable.addEventListener('input', function (e) {
            if (e.target.classList.contains('po-item-qty') || e.target.classList.contains('po-item-price')) {
                calculatePOTotals();
            }
        });
        calculatePOTotals();
    }

    // ============================================================
    // FITUR NILAI PLUS: AI VISION SURAT JALAN SCANNER
    // ============================================================
    const btnTriggerAIScan = document.getElementById('btn-ai-scan');
    const aiScanFileInput = document.getElementById('ai-scan-file');
    const doNumberInput = document.getElementById('delivery_order_number');
    const grNotesInput = document.getElementById('notes');

    if (btnTriggerAIScan && doNumberInput) {
        btnTriggerAIScan.addEventListener('click', function () {
            // Animasi loading tombol
            const originalHtml = btnTriggerAIScan.innerHTML;
            btnTriggerAIScan.disabled = true;
            btnTriggerAIScan.innerHTML = `
                <span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                AI Vision Memindai Dokumen...
            `;

            // Simulasi FormData
            const formData = new FormData();
            if (aiScanFileInput && aiScanFileInput.files.length > 0) {
                formData.append('file', aiScanFileInput.files[0]);
            }

            fetch('/api/ai-scan-do', {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                btnTriggerAIScan.disabled = false;
                btnTriggerAIScan.innerHTML = originalHtml;

                if (data.success) {
                    doNumberInput.value = data.data.detected_do_number;
                    if (grNotesInput && (!grNotesInput.value || grNotesInput.value.trim() === '')) {
                        grNotesInput.value = data.data.ai_notes;
                    }

                    // Tampilkan notifikasi visual modern
                    const alertPlaceholder = document.getElementById('ai-alert-placeholder');
                    if (alertPlaceholder) {
                        alertPlaceholder.innerHTML = `
                            <div class="alert alert-success alert-dismissible fade show shadow-sm" role="alert">
                                <i class="bi bi-robot me-2"></i>
                                <strong>AI Smart Vision Berhasil!</strong> Nomor Surat Jalan terdeteksi: <code>${data.data.detected_do_number}</code> (Confidence: ${data.data.confidence_score}).
                                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                            </div>
                        `;
                    }
                }
            })
            .catch(err => {
                btnTriggerAIScan.disabled = false;
                btnTriggerAIScan.innerHTML = originalHtml;
                console.error(err);
                alert('Gagal menghubungi modul AI scanner.');
            });
        });
    }
});
