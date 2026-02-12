from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

# --------------------------
# Choices Configuration
# --------------------------
# Define choices for various dropdown fields in the Shipment model to ensure data consistency.

PRICE_TERMS_CHOICES = [
    ('DAP', 'DAP'),
    ('LC', 'LC'),
    ('TT', 'TT'),
    ('N/A', 'N/A'),
]

PAYMENT_TERMS_CHOICES = [
    ('CFR', 'CFR'),
    ('CIF', 'CIF'),
    ('FOB', 'FOB'),
    ('EXW', 'EXW'),
    ('N/A', 'N/A'),
]

BANK_CHOICES = [
    ('Nabil', 'Nabil Bank'),
    ('NIC', 'NIC Asia Bank'),
    ('SBI', 'Nepal SBI Bank'),
    ('Global', 'Global IME Bank'),
    ('Prabhu', 'Prabhu Bank'),
    ('Machha', 'Machhapuchhre Bank'),
    ('Sanima', 'Sanima Bank'),
    ('Mega', 'Mega Bank'),
    ('Kumari', 'Kumari Bank'),
    ('N/A', 'N/A'),
]

INSURANCE_COMPANY_CHOICES = [
    ('IME', 'IME Life Insurance Company Limited'),
    ('Neco', 'Neco Insurance Ltd.'),
    ('Sanima', 'Sanima GIC Insurance Ltd.'),
    ('Salico', 'Sagarmatha Lumbini Insurance Company Ltd.'),
    ('Sidd', 'Siddhartha Premier Insurance Ltd.'),
    ('N/A', 'N/A'),
]

CURRENCY_CHOICES = [
    ('$', 'USD'),
    ('₹', 'INR'),
    ('रु ', 'NPR'),
]

VANSHAR_CHOICES = [
    ('Mechi', 'Mechi'),
    ('Birgunj', 'Birgunj'),
    ('Biratnagar', 'Biratnagar'),
    ('Tatopani', 'Tatopani'),
    ('TIA', 'Tribhuvan International Airport'),
    ('N/A', 'N/A'),
]

YATAYAT_CHOICES = [
    ('Mechi', 'Mechi'),
    ('Koshi', 'Koshi'),
    ('Sagarmatha', 'Sagarmatha'),
    ('Janakpur', 'Janakpur'),
    ('Bagmati', 'Bagmati'),
    ('Narayani', 'Narayani'),
    ('Gandaki', 'Gandaki'),
    ('Dhaulagiri', 'Dhaulagiri'),
    ('Lumbini', 'Lumbini'),
    ('Rapti', 'Rapti'),
    ('Bheri', 'Bheri'),
    ('Karnali', 'Karnali'),
    ('Seti', 'Seti'),
    ('Mahakali', 'Mahakali'),
    ('N/A', 'N/A'),
]


# --------------------------
# Shipment Model
# --------------------------
class Shipment(models.Model):
    """
    Represents a shipment record in the system.
    Stores all necessary details regarding logistics, payments, and dates.
    """
    applicant = models.CharField(max_length=20)
    invoice_no = models.CharField(max_length=20, unique=True)

    bank_name = models.CharField(max_length=20, choices=BANK_CHOICES)
    bank_ref_no = models.CharField(max_length=20, blank=True, null=True)

    insurance_company = models.CharField(
        max_length=50,
        choices=INSURANCE_COMPANY_CHOICES,
        blank=True,
        null=True,
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES, default='USD')

    price_terms = models.CharField(max_length=10, choices=PRICE_TERMS_CHOICES)
    payment_terms = models.CharField(max_length=10, choices=PAYMENT_TERMS_CHOICES)

    dispatch_date = models.DateField()
    doc_received_date = models.DateField(blank=True, null=True)
    eta_date = models.DateField(blank=True, null=True)
    settlement_date = models.DateField(blank=True, null=True)
    margin_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    margin_date = models.DateField(blank=True, null=True)
    customs_entry_date = models.DateField(blank=True, null=True)
    
    doc_to_bank = models.DateField(blank=True, null=True)
    
    pp_no = models.CharField(max_length=20, blank=True, null=True)
    
    vanshar = models.CharField(
        max_length=50,
        choices=VANSHAR_CHOICES,
        blank=True,
        null=True
    )


    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='shipments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-dispatch_date']
        verbose_name = 'Shipment'
        verbose_name_plural = 'Shipments'

    def __str__(self):
        """Returns the string representation of the shipment."""
        return f"{self.invoice_no} - {self.applicant}"

    def amount_display(self):
        """
        Returns a formatted string of the amount with its currency symbol.
        Example: $ 100.00
        """
        if self.amount and self.currency:
            return f"{self.currency} {self.amount}"
        return "N/A"

    amount_display.short_description = "Amount"


# --------------------------
# Shipment Yatayat Model (Child)
# --------------------------
class ShipmentYatayat(models.Model):
    """
    Represents a specific transport/yatayat detail associated with a shipment.
    A shipment can have multiple yatayat records.
    """
    shipment = models.ForeignKey(
        Shipment, 
        on_delete=models.CASCADE, 
        related_name='yatayats'
    )
    yatayat = models.CharField(
        max_length=50,
        choices=YATAYAT_CHOICES,
        blank=True,
        null=True
    )
    chitti_file = models.FileField(
        upload_to='shipment_chittis/%Y/%m/',
        blank=True,
        null=True
    )
    date_issued = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.yatayat or 'N/A'} for {self.shipment.invoice_no}"

    def get_file_url(self):
        """Returns the URL of the uploaded chitti file if it exists."""
        return self.chitti_file.url if self.chitti_file else None


# --------------------------
# Ticket Model
# --------------------------
class Ticket(models.Model):
    """
    Represents a support ticket raised by a user.
    Includes auto-incrementing custom ticket IDs (Year-Sequence).
    """
    class Category(models.TextChoices):
        TECHNICAL_ISSUE = 'technical', 'Technical Issue'
        BILLING_QUESTION = 'billing', 'Billing Question'
        FEATURE_REQUEST = 'feature', 'Feature Request'
        GENERAL_INQUIRY = 'general', 'General Inquiry'

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        URGENT = 'urgent', 'Urgent'

    ticket_id = models.CharField(max_length=15, unique=True, editable=False)
    raised_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    subject = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=Category.choices)
    priority = models.CharField(max_length=10, choices=Priority.choices)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """
        Override save method to generate custom ticket_id.
        Format: YYYY-XXXX (e.g., 2024-0001)
        """
        try:
            if not self.ticket_id:
                current_year = timezone.now().year
                last_ticket = (
                    Ticket.objects
                    .filter(ticket_id__startswith=f'{current_year}-')
                    .order_by('ticket_id')
                    .last()
                )

                last_number = int(last_ticket.ticket_id.split('-')[1]) if last_ticket else 0
                self.ticket_id = f'{current_year}-{last_number + 1:04d}'

            super().save(*args, **kwargs)

        except Exception:
            logger.error(
                "Ticket save failed",
                exc_info=True
            )
            raise

    def __str__(self):
        return f'Ticket #{self.ticket_id} - {self.subject}'


