from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.core.files.uploadedfile import UploadedFile
from django.utils import timezone

from .models import Shipment, Ticket, ShipmentYatayat

# =========================================================
# CONSTANTS
# =========================================================
TODAY = timezone.now().date()
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB
DATE_FORMAT_URL = '%d/%m/%Y'

# =========================================================
# SHIPMENT FORM
# =========================================================
class ShipmentForm(forms.ModelForm):
    """
    Form for creating and updating Shipment records.
    Customizes widgets for Date inputs and styling.
    Includes validation for dates and amounts.
    """
    class Meta:
        model = Shipment
        exclude = ['created_by']
        widgets = {
            'dispatch_date': forms.DateInput(
                format=DATE_FORMAT_URL,
                attrs={
                    'class': 'form-control date-field',
                    'placeholder': 'DD/MM/YYYY',
                    'autocomplete': 'off'
                }
            ),
            'doc_received_date': forms.DateInput(
                format=DATE_FORMAT_URL,
                attrs={
                    'class': 'form-control date-field',
                    'placeholder': 'DD/MM/YYYY',
                    'autocomplete': 'off'
                }
            ),
            'eta_date': forms.DateInput(
                format=DATE_FORMAT_URL,
                attrs={
                    'class': 'form-control date-field',
                    'placeholder': 'DD/MM/YYYY',
                    'autocomplete': 'off'
                }
            ),
            'settlement_date': forms.DateInput(
                format=DATE_FORMAT_URL,
                attrs={
                    'class': 'form-control date-field',
                    'placeholder': 'DD/MM/YYYY',
                    'autocomplete': 'off'
                }
            ),
            'customs_entry_date': forms.DateInput(
                format=DATE_FORMAT_URL,
                attrs={
                    'class': 'form-control date-field',
                    'placeholder': 'DD/MM/YYYY',
                    'autocomplete': 'off'
                }
            ),
            'margin_date': forms.DateInput(
                format=DATE_FORMAT_URL,
                attrs={
                    'class': 'form-control date-field',
                    'placeholder': 'DD/MM/YYYY',
                    'autocomplete': 'off'
                }
            ),
            'doc_to_bank': forms.DateInput(
                format=DATE_FORMAT_URL,
                attrs={
                    'class': 'form-control date-field',
                    'placeholder': 'DD/MM/YYYY',
                    'autocomplete': 'off'
                }
            ),

            # --- rest unchanged ---
            'price_terms': forms.Select(attrs={'class': 'form-select'}),
            'payment_terms': forms.Select(attrs={'class': 'form-select'}),
            'bank_name': forms.Select(attrs={'class': 'form-select'}),
            'insurance_company': forms.Select(attrs={'class': 'form-select'}),
            'invoice_no': forms.TextInput(attrs={'class': 'form-control invoice-field'}),
            'bank_ref_no': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control amount-field', 'step': '0.01', 'min': '0'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'pp_no': forms.TextInput(attrs={'class': 'form-control'}),
            'applicant': forms.TextInput(attrs={'class': 'form-control'}),
            'vanshar': forms.Select(attrs={'class': 'form-select'}),
            'margin_amount': forms.NumberInput(attrs={'class': 'form-control amount-field', 'step': '0.01', 'min': '0'}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in [
            'dispatch_date',
            'doc_received_date',
            'eta_date',
            'settlement_date',
            'customs_entry_date',
            'doc_to_bank',
            'margin_date',
        ]:
            self.fields[field].input_formats = [DATE_FORMAT_URL]
    
    def clean_margin_date(self):
        """Ensure margin date is not in the future."""
        margin_date = self.cleaned_data.get('margin_date')
        if margin_date and margin_date > timezone.now().date():
            raise ValidationError("Margin date cannot be in the future.")
        return margin_date
    
    def clean_dispatch_date(self):
        """Ensure dispatch date is not in the future."""
        date = self.cleaned_data.get('dispatch_date')
        if date and date > timezone.now().date():
            raise ValidationError("Dispatch date cannot be in the future.")
        return date

    def clean_doc_received_date(self):
        """Ensure document received date is not in the future."""
        date = self.cleaned_data.get('doc_received_date')
        if date and date > timezone.now().date():
            raise ValidationError("Document received date cannot be in the future.")
        return date

    def clean_customs_entry_date(self):
        """Ensure customs entry date is not in the future."""
        date = self.cleaned_data.get('customs_entry_date')
        if date and date > timezone.now().date():
            raise ValidationError("Customs entry date cannot be in the future.")
        return date

    def clean_doc_to_bank(self):
        """Ensure document-to-bank date is not in the future."""
        date = self.cleaned_data.get('doc_to_bank')
        if date and date > timezone.now().date():
            raise ValidationError("Document to bank date cannot be in the future.")
        return date
    
    def clean_amount(self):
        """Ensure transaction amount is non-negative."""
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount < 0:
            raise ValidationError("Amount cannot be negative.")
        return amount

    def clean_margin_amount(self):
        """Ensure margin amount is non-negative."""
        margin_amount = self.cleaned_data.get('margin_amount')
        if margin_amount is not None and margin_amount < 0:
            raise ValidationError("Margin amount cannot be negative.")
        return margin_amount


# =========================================================
# SHIPMENT YATAYAT FORM
# =========================================================
class ShipmentYatayatForm(forms.ModelForm):
    """
    Form for adding/editing a Yatayat (Transport) details within a shipment.
    Handled primarily via FormSet.
    """
    class Meta:
        model = ShipmentYatayat
        fields = ['yatayat', 'chitti_file']
        widgets = {
            'yatayat': forms.Select(attrs={'class': 'form-select'}),
            'chitti_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_chitti_file(self):
        """
        Validate file upload:
        - Max size: 5MB
        - File type: PDF only
        """
        file = self.cleaned_data.get('chitti_file')
        if file:
            if file.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError("File size must not exceed 5 MB.")
            if not file.name.lower().endswith('.pdf'):
                raise ValidationError("Only PDF files are allowed.")
        return file


# =========================================================
# YATAYAT FORMSET
# =========================================================
ShipmentYatayatFormSet = inlineformset_factory(
    Shipment,
    ShipmentYatayat,
    form=ShipmentYatayatForm,
    extra=1,
    can_delete=True
)


# =========================================================
# TICKET FORM
# =========================================================
class TicketForm(forms.ModelForm):
    """
    Form for raising a new support ticket.
    """
    class Meta:
        model = Ticket
        fields = ['subject', 'category', 'priority', 'description']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter a brief summary'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 5, 
                'placeholder': 'Describe your issue in detail...'
            }),
        }

    def clean_subject(self):
        """Ensure subject has valid length."""
        subject = self.cleaned_data.get('subject', '').strip()
        if len(subject) < 5:
            raise ValidationError("Subject must be at least 5 characters long.")
        return subject
