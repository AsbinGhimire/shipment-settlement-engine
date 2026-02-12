import logging
from datetime import timedelta

from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView,
    TemplateView, FormView
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin
)
from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .models import Shipment, Ticket, ShipmentYatayat
from .forms import ShipmentForm, TicketForm, ShipmentYatayatFormSet
from shipments.mixins import RBACContextMixin

logger = logging.getLogger(__name__)

# --------------------
# HOME
# --------------------
def home(request):
    """
    Renders the public landing page of the application.
    """
    logger.info("Home page accessed")
    return render(request, 'landingpage/index.html')


# --------------------
# SHIPMENT LIST
# --------------------
class ShipmentListView(LoginRequiredMixin, RBACContextMixin, ListView):
    """
    Displays a list of shipments.
    - Staff/Admin users see all shipments (Administrator View).
    - Regular users see only their own shipments (User View).
    """
    model = Shipment
    context_object_name = 'shipments'

    def get_queryset(self):
        """
        Returns the queryset based on user permissions.
        Annotates 'chitti_count' to track related files.
        """
        try:
            user = self.request.user
            qs = Shipment.objects.annotate(
                chitti_count=Count('yatayats', filter=Q(yatayats__chitti_file__isnull=False) & ~Q(yatayats__chitti_file=''))
            ).prefetch_related('yatayats').order_by('-id')

            if user.is_staff or user.has_perm('shipments.view_shipment'):
                return qs

            return qs.filter(created_by=user)

        except Exception:
            logger.error(
                "Failed to load shipment list",
                exc_info=True
            )
            raise

    def get_template_names(self):
        """
        Selects template based on user role to show appropriate UI.
        """
        if self.request.user.is_staff or self.request.user.has_perm('shipments.change_shipment'):
            return ['shipments/admin_list.html']
        return ['shipments/user_list.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['header'] = (
            "All Shipments (Administrator View)"
            if self.request.user.is_staff
            else "My Shipment Records"
        )
        return context


# --------------------
# CREATE SHIPMENT
# --------------------
class ShipmentCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    RBACContextMixin,
    CreateView
):
    """
    Handles the creation of a new shipment record along with its related yatayat (transport) details.
    Uses 'ShipmentForm' for the main record and 'ShipmentYatayatFormSet' for related items.
    """
    model = Shipment
    form_class = ShipmentForm
    template_name = 'shipments/add.html'
    success_url = reverse_lazy('shipments:shipment_list')
    permission_required = 'shipments.add_shipment'

    def get_context_data(self, **kwargs):
        """
        Adds the Yatayat formset to the context context.
        """
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['yatayat_formset'] = ShipmentYatayatFormSet(
                self.request.POST,
                self.request.FILES,
                prefix='yatayat'
            )
        else:
            context['yatayat_formset'] = ShipmentYatayatFormSet(prefix='yatayat')
        return context

    def form_valid(self, form):
        """
        Validates both the main form and the formset.
        Saves data transactionally to ensure integrity.
        """
        context = self.get_context_data()
        yatayat_formset = context['yatayat_formset']

        if not yatayat_formset.is_valid():
            logger.warning("Yatayat formset invalid during shipment creation")
            return self.form_invalid(form)

        try:
            with transaction.atomic():
                form.instance.created_by = self.request.user
                self.object = form.save()

                # Save Yatayats
                yatayats = yatayat_formset.save(commit=False)
                for obj in yatayat_formset.deleted_objects:
                    obj.delete()
                
                for yatayat in yatayats:
                    yatayat.shipment = self.object
                    yatayat.save()

            logger.info(
                f"Shipment created | ID={self.object.id} | User={self.request.user}"
            )

            messages.success(
                self.request,
                f"Shipment '{self.object.invoice_no}' added successfully."
            )
            return super().form_valid(form)

        except Exception:
            logger.error(
                "Error creating shipment",
                exc_info=True
            )
            raise


# --------------------
# UPDATE SHIPMENT
# --------------------
class ShipmentUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    RBACContextMixin,
    UpdateView
):
    """
    Handles updating an existing shipment and its related yatayat details.
    """
    model = Shipment
    form_class = ShipmentForm
    template_name = 'shipments/edit.html'
    success_url = reverse_lazy('shipments:shipment_list')
    permission_required = 'shipments.change_shipment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['yatayat_formset'] = ShipmentYatayatFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object,
                prefix='yatayat'
            )
        else:
            context['yatayat_formset'] = ShipmentYatayatFormSet(
                instance=self.object,
                prefix='yatayat'
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        yatayat_formset = context['yatayat_formset']

        if not yatayat_formset.is_valid():
            return self.form_invalid(form)

        try:
            with transaction.atomic():
                self.object = form.save()

                yatayats = yatayat_formset.save(commit=False)
                for obj in yatayat_formset.deleted_objects:
                    obj.delete()
                
                for yatayat in yatayats:
                    yatayat.shipment = self.object
                    yatayat.save()

            logger.info(
                f"Shipment updated | ID={self.object.id} | User={self.request.user}"
            )

            messages.success(
                self.request,
                f"Shipment '{self.object.invoice_no}' updated successfully."
            )
            return super().form_valid(form)

        except Exception:
            logger.error(
                f"Error updating shipment | ID={self.object.id}",
                exc_info=True
            )
            raise

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


# --------------------
# DELETE SHIPMENT
# --------------------
class ShipmentDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    RBACContextMixin,
    DeleteView
):
    """
    Handles the deletion of a shipment record.
    Logs the action for audit purposes.
    """
    model = Shipment
    template_name = 'shipments/delete.html'
    success_url = reverse_lazy('shipments:shipment_list')
    permission_required = 'shipments.delete_shipment'

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()

        logger.warning(
            f"Shipment DELETE initiated | ID={obj.id} | User={request.user}"
        )

        response = super().delete(request, *args, **kwargs)

        logger.warning(
            f"Shipment DELETED | ID={obj.id} | User={request.user}"
        )

        messages.success(
            request,
            f"Shipment '{obj.invoice_no}' and all related chitti files deleted."
        )
        return response


# --------------------
# HELPLINE / TICKETS
# --------------------
class HelpLineView(LoginRequiredMixin, RBACContextMixin, FormView):
    """
    View for submitting support tickets/helpline requests.
    Includes a cooldown mechanism (5 minutes) to prevent spamming.
    Sends email notifications upon successful submission.
    """
    template_name = 'shipments/helpline.html'
    form_class = TicketForm
    success_url = reverse_lazy('shipments:helpline')

    def form_valid(self, form):
        user = self.request.user
        five_minutes_ago = timezone.now() - timedelta(minutes=5)
        
        # Check for recent tickets
        last_ticket = Ticket.objects.filter(
            raised_by=user,
            created_at__gte=five_minutes_ago
        ).order_by('-created_at').first()

        if last_ticket:
            elapsed = (timezone.now() - last_ticket.created_at).total_seconds()
            remaining_seconds = int(300 - elapsed)
            
            if remaining_seconds > 0:
                from django.utils.safestring import mark_safe
                
                # Format initial text
                mins, secs = divmod(remaining_seconds, 60)
                if mins > 0:
                    time_str = f"{mins}m {secs}s"
                else:
                    time_str = f"{secs}s"

                msg = f"Please wait before submitting another ticket. Time remaining: <span id='countdown' data-seconds='{remaining_seconds}'>{time_str}</span>"
                messages.warning(self.request, mark_safe(msg))
                
                # Return with cooldown context
                return self.render_to_response(self.get_context_data(
                    form=form, 
                    cooldown_active=True, 
                    remaining_seconds=remaining_seconds
                ))

        # ✅ CREATE TICKET SAFELY
        with transaction.atomic():
            ticket = form.save(commit=False)
            ticket.raised_by = user
            ticket.save()

        # 📧 CONSTRUCT FULL EMAIL CONTENT
        subject_text = form.cleaned_data.get('subject')
        category = form.cleaned_data.get('category')
        priority = form.cleaned_data.get('priority')
        description = form.cleaned_data.get('description')

        email_body = (
            f"--- ACCOUNTEASE TICKET RAISED ---\n\n"
            f"Ticket ID: #{ticket.id}\n"
            f"Raised By: {user.username} ({user.email})\n"
            f"Category: {category}\n"
            f"Priority: {priority}\n"
            f"Subject: {subject_text}\n"
            f"Description:\n{description}\n\n"
        )

        try:
            send_mail(
                subject=f"[{priority.upper()}] New Ticket: {subject_text}",
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['infivity.labs@gmail.com'],
                fail_silently=False,
            )
            messages.success(self.request, "Ticket submitted successfully.")
        except Exception as e:
            # Helpful for debugging, but keeps the app running
            print(f"Email error: {e}")
            messages.warning(
                self.request,
                "Ticket submitted, but email notification failed."
            )

        return redirect(self.success_url)


# --------------------
# AJAX: CHITTI FILES
# --------------------
def get_chitti_files(request, shipment_id):
    """
    AJAX handler to fetch attached files (chitti) for a specific shipment.
    Returns JSON response containing file URLs and details.
    """
    try:
        shipment = get_object_or_404(Shipment, id=shipment_id)
        
        files_data = []
        for yatayat in shipment.yatayats.all():
            if yatayat.chitti_file:
                files_data.append({
                    'display_name': yatayat.chitti_file.name.split('/')[-1],
                    'url': yatayat.chitti_file.url,
                    'date': yatayat.date_issued.strftime('%Y-%m-%d'),
                    'vanshar': shipment.vanshar or 'N/A' # Displaying Shipment Vanshar
                })

        return JsonResponse({'files': files_data})

    except Exception:
        logger.error(
            f"Failed to fetch chitti files | ShipmentID={shipment_id}",
            exc_info=True
        )
        return JsonResponse({'files': []}, status=500)

# --------------------
# STATIC ADMIN VIEWS
# --------------------
class ReportsView(LoginRequiredMixin, UserPassesTestMixin, RBACContextMixin, TemplateView):
    """
    Renders the Reports page. Accessible only to Superusers and Admin group.
    """
    template_name = 'shipments/reports.html'

    def test_func(self):
        # allow superuser or Administrator group
        user = self.request.user
        return user.is_superuser or user.groups.filter(name='Admin').exists()


class ClientsView(LoginRequiredMixin, UserPassesTestMixin, RBACContextMixin, TemplateView):
    """
    Renders the Clients page. Accessible only to Superusers and Admin group.
    """
    template_name = 'shipments/clients.html'

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.groups.filter(name='Admin').exists()


