document.addEventListener('DOMContentLoaded', function () {

    /* ===== Input Masking & Validation ===== */
    
    // 1. Date Fields (dd/mm/yyyy)
    const dateFields = document.querySelectorAll(".date-field");
    dateFields.forEach(function(field) {
        // Init Flatpickr (Calendar)
        if(typeof flatpickr !== 'undefined') {
            let config = {
                dateFormat: "d/m/Y",
                allowInput: true,
                disableMobile: "true", // Force custom input on mobile
                onClose: function(_, __, instance) {
                    // Trigger input event to ensure frameworks catch the change
                    instance.input.dispatchEvent(new Event('input', { bubbles: true }));
                }
            };
            
            // Restrict specific date fields to past/today dates
            const restrictedFields = [
                'id_margin_date',
                'id_dispatch_date',
                'id_doc_received_date',
                'id_customs_entry_date',
                'id_doc_to_bank'
            ];
            
            if (restrictedFields.includes(field.id)) {
                config.maxDate = "today";
            }
            
            flatpickr(field, config);
        }

        // Init Cleave (Input Masking)
        if(typeof Cleave !== 'undefined') {
            new Cleave(field, {
                date: true,
                delimiter: '/',
                datePattern: ['d', 'm', 'Y']
            });
        }

        // Fallback: Remove non-numeric/slash chars manually if Cleave fails
        field.addEventListener('input', function(e) {
            let val = e.target.value;
            e.target.value = val.replace(/[^0-9\/]/g, '');
        });
    });

    // 2. Amount Fields (Currency formatting)
    const amountFields = document.querySelectorAll(".amount-field");
    if(amountFields.length > 0 && typeof Cleave !== 'undefined') {
        amountFields.forEach(function(field) {
            new Cleave(field, {
                numeral: true,
                numeralThousandsGroupStyle: 'thousand',
                numeralDecimalScale: 2
            });
        });
    }

    // 3. Invoice Fields (Uppercase)
    const invoiceFields = document.querySelectorAll(".invoice-field");
    invoiceFields.forEach(function(field) {
        field.addEventListener('input', function(e) {
            e.target.value = e.target.value.toUpperCase();
        });
    });

    /* ===== Formset Add ===== */
    const addBtn = document.getElementById('add-yatayat-btn'); 
    const container = document.getElementById('yatayat-formset-container');
    const totalForms = document.getElementById('id_yatayat-TOTAL_FORMS');
    const templateEl = document.getElementById('empty-form-template');

    if (addBtn && container && totalForms && templateEl) {
        const template = templateEl.innerHTML;
        addBtn.addEventListener('click', function () {
            const index = parseInt(totalForms.value);
            container.insertAdjacentHTML(
                'beforeend',
                template.replace(/__prefix__/g, index)
            );
            totalForms.value = index + 1;
        });
    }

    /* ===== Submit Loader ===== */
    const form = document.getElementById("shipmentForm");
    const submitBtn = document.getElementById("submitBtn");
    const btnText = document.getElementById("btnText");
    const btnLoading = document.getElementById("btnLoading");

    if (form && submitBtn) {
        form.addEventListener("submit", function (e) {
            if (!form.checkValidity()) return;
            
            // Additional check for negative amounts (security/redundancy)
            const amounts = form.querySelectorAll(".amount-field");
            let hasError = false;
            amounts.forEach(input => {
                const val = parseFloat(input.value.replace(/,/g, ''));
                if (val < 0) {
                    hasError = true;
                    input.classList.add("is-invalid");
                } else {
                    input.classList.remove("is-invalid");
                }
            });

            if (hasError) {
                e.preventDefault();
                alert("Please ensure all amounts are non-negative.");
                return;
            }

            submitBtn.disabled = true;
            if(btnText) btnText.classList.add("d-none");
            if(btnLoading) btnLoading.classList.remove("d-none");
        });
    }
});
