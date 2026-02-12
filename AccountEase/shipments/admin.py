from django.contrib import admin
from django.utils.html import format_html

from .models import Shipment, ShipmentYatayat, Ticket
from .forms import ShipmentYatayatForm


# =====================================================
# SHIPMENT YATAYAT INLINE
# =====================================================
class ShipmentYatayatInline(admin.TabularInline):
    """
    Inline admin interface for ShipmentYatayat.
    Allows managing yatayats and chitti files directly within the Shipment admin page.
    """
    model = ShipmentYatayat
    form = ShipmentYatayatForm
    extra = 1
    fields = ('yatayat', 'chitti_file', 'date_issued', 'file_link')
    readonly_fields = ('date_issued', 'file_link')

    def file_link(self, obj):
        """
        Provides a clickable link to view the PDF file.
        """
        if obj.pk and obj.chitti_file:
            return format_html(
                '<a href="{}" target="_blank">📄 View PDF</a>',
                obj.chitti_file.url
            )
        return "—"

    file_link.short_description = "File"


# =====================================================
# SHIPMENT ADMIN
# =====================================================
@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Shipment model.
    Organizes fields into logical fieldsets for better usability.
    Includes search, filter, and ordering capabilities.
    """
    list_display = (
        'invoice_no',
        'applicant',
        'vanshar',
        'bank_name',
        'amount_display',
        'currency',
        'created_by',
        'created_at',
    )

    list_filter = (
        'bank_name',
        'price_terms',
        'payment_terms',
        'insurance_company',
        'currency',
        'dispatch_date',
    )

    search_fields = (
        'invoice_no',
        'applicant',
        'bank_name',
        'pp_no',
    )

    ordering = ('-created_at',)
    readonly_fields = ('created_by', 'created_at', 'updated_at')

    fieldsets = (
        ('Shipment Details', {
            'fields': (
                'invoice_no',
                'applicant',
                'vanshar',
                'price_terms',
                'payment_terms',
                'amount',
                'currency',
            )
        }),
        ('Bank & Insurance', {
            'fields': (
                'bank_name',
                'bank_ref_no',
                'insurance_company',
                'pp_no',
            )
        }),
        ('Dates', {
            'fields': (
                'dispatch_date',
                'doc_received_date',
                'eta_date',
                'settlement_date',
                'customs_entry_date',
                'doc_to_bank',
                'margin_amount',
                'margin_date',
            )
        }),
        ('Meta Information', {
            'fields': (
                'created_by',
                'created_at',
                'updated_at',
            )
        }),
    )

    inlines = [ShipmentYatayatInline]

    def save_model(self, request, obj, form, change):
        """
        Automatically set the 'created_by' field to the current user on creation.
        """
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# =====================================================
# SUPPORT TICKET ADMIN
# =====================================================
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """
    Admin configuration for Support Tickets.
    """
    list_display = (
        'ticket_id',
        'subject',
        'priority',
        'category',
        'raised_by',
        'created_at',
    )

    list_filter = ('priority', 'category', 'created_at')
    search_fields = ('ticket_id', 'subject', 'raised_by__username')
