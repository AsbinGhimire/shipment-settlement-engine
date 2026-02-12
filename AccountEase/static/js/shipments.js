// SHIPMENT LIST LOGIC
document.addEventListener('DOMContentLoaded', () => {
    // 1. Chitti Modal Logic
    const modal = document.getElementById('chittiModal');
    if(modal) {
        modal.addEventListener('show.bs.modal', e => {
            const btn = e.relatedTarget;
            const id = btn.dataset.shipmentId;
            const invoice = btn.dataset.invoiceNo;
            const list = document.getElementById('chitti-files-list');
            
            document.getElementById('modalTitle').innerText = `Files for Invoice: ${invoice}`;
            list.innerHTML = `<div class="text-center py-4"><div class="spinner-border spinner-border-sm text-primary"></div></div>`;

            fetch(`/shipments/shipment-files/${id}/`)
                .then(r => r.json())
                .then(d => {
                    list.innerHTML = '';
                    if (!d.files?.length) {
                        list.innerHTML = `<div class="p-4 text-center text-muted small">No files available</div>`;
                        return;
                    }
                    d.files.forEach(f => {
                        list.innerHTML += `
                            <div class="list-group-item d-flex justify-content-between align-items-center p-3">
                                <div class="d-flex align-items-center">
                                    <i class="bi bi-file-earmark-pdf text-danger fs-5 me-3"></i>
                                    <div>
                                        <div class="fw-bold small text-dark">${f.display_name}</div>
                                        <div style="font-size: 0.65rem;" class="text-muted">${f.date}</div>
                                    </div>
                                </div>
                                <a href="${f.url}" target="_blank" class="btn btn-sm btn-primary px-3 rounded-pill" style="font-size: 0.7rem;">
                                    Open <i class="bi bi-box-arrow-up-right ms-1"></i>
                                </a>
                            </div>`;
                    });
                })
                .catch(() => {
                    list.innerHTML = `<div class="p-3 text-center text-danger small">Error loading files</div>`;
                });
        });
    }

    // 2. Search and Filtering Logic
    const $ = id => document.getElementById(id);

    const searchInput = $('invoiceSearch');
    const statusFilter = $('statusFilter');
    const etaStart = $('etaStart');
    const etaEnd = $('etaEnd');
    const etaToggleBtn = $('etaToggleBtn');
    const etaFilterBox = $('etaFilterBox');
    const closeEtaBox = $('closeEtaBox');
    const clearBtn = $('clearAllFilters');
    const counter = $('rowCountDisplay');

    if (!searchInput) return; // Exit if filters are not present

    const rows = [...document.querySelectorAll('table tbody tr:not(.empty-row)')];

    if (typeof Cleave !== 'undefined') {
        [etaStart, etaEnd].forEach(el => {
            new Cleave(el, {
                date: true,
                delimiter: '/',
                datePattern: ['d','m','Y']
            });
        });
    }

    function parseDMY(v) {
        if (!v || v.length !== 10) return null;
        const [d,m,y] = v.split('/');
        return new Date(y, m - 1, d);
    }

    function normalize(t) {
        return (t || '').toLowerCase().trim();
    }

    /* 🔥 SEARCH = INVOICE/APPLICANT COLUMN ONLY (NEW INDEX 1) */
    function rowMatchesSearch(row, query) {
        if (!query) return true;

        const invoiceCellIndex = 1; // 👈 INVOICE/APPLICANT MERGED COLUMN
        const invoiceCell = row.cells[invoiceCellIndex];
        if (!invoiceCell) return false;
        
        return normalize(invoiceCell.innerText).includes(query);
    }

    function applyFilters() {
        const query = normalize(searchInput.value);
        const status = normalize(statusFilter.value);
        const startDate = parseDMY(etaStart.value);
        const endDate = parseDMY(etaEnd.value);

        let visibleCount = 0;

        rows.forEach(row => {
            let visible = true;

            if (!rowMatchesSearch(row, query)) visible = false;

            if (status) {
                // Professional check: Does the row contain any element with the 'badge-pending' class?
                const hasPendingBadge = row.querySelector('.badge-pending') !== null;
                
                if (status === 'unsettled') {
                    if (!hasPendingBadge) visible = false;
                } else if (status === 'settled') {
                    if (hasPendingBadge) visible = false;
                }
            }

            if (startDate || endDate) {
                const etaText = row.cells[7]?.innerText || ''; // 👈 ETA column now at index 7
                const rowDate = parseDMY(etaText);
                if (!rowDate) visible = false;
                if (startDate && rowDate < startDate) visible = false;
                if (endDate && rowDate > endDate) visible = false;
            }

            row.style.display = visible ? '' : 'none';
            if (visible) visibleCount++;
        });

        counter.textContent =
            visibleCount === rows.length
                ? "Showing all records"
                : `Showing ${visibleCount} of ${rows.length} records`;
    }

    function debounce(fn, d = 250) {
        let t;
        return () => { clearTimeout(t); t = setTimeout(fn, d); };
    }

    const debouncedFilter = debounce(applyFilters);

    if (etaToggleBtn) {
        etaToggleBtn.onclick = e => {
            e.stopPropagation();
            etaFilterBox.classList.toggle('show');
            etaToggleBtn.classList.toggle('active');
        };
    }

    if (closeEtaBox) {
        closeEtaBox.onclick = () => etaFilterBox.classList.remove('show');
    }

    document.addEventListener('click', e => {
        if (etaFilterBox && !etaFilterBox.contains(e.target) && !etaToggleBtn.contains(e.target)) {
            etaFilterBox.classList.remove('show');
            etaToggleBtn.classList.remove('active');
        }
    });

    searchInput.addEventListener('input', debouncedFilter);
    statusFilter.addEventListener('change', applyFilters);
    etaStart.addEventListener('input', applyFilters);
    etaEnd.addEventListener('input', applyFilters);

    clearBtn.onclick = () => {
        searchInput.value = '';
        statusFilter.value = '';
        etaStart.value = '';
        etaEnd.value = '';
        applyFilters();
    };
});
