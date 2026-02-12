from rest_framework import serializers
from .models import Shipment, ShipmentYatayat


class ShipmentYatayatSerializer(serializers.ModelSerializer):
    """
    Serializer for ShipmentYatayat model.
    Handles serialization of yatayat details including file URLs and display names.
    Includes helper methods to construct absolute URLs for stored files.
    """
    url = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    date = serializers.DateField(source='date_issued', format='%Y-%m-%d', read_only=True)

    class Meta:
        model = ShipmentYatayat
        fields = ['id', 'yatayat', 'url', 'display_name', 'date']

    def to_representation(self, instance):
        """
        Customize output to return 'N/A' if yatayat name is missing.
        """
        data = super().to_representation(instance)
        if not data.get('yatayat'):
            data['yatayat'] = "N/A"
        return data

    def get_url(self, obj):
        """
        Return the absolute URL of the uploaded chitti file.
        Ensures the URL is complete with domain if request context is available.
        """
        request = self.context.get('request')
        if obj.chitti_file:
            if request:
                return request.build_absolute_uri(obj.chitti_file.url)
            return obj.chitti_file.url
        return None

    def get_display_name(self, obj):
        """
        Return only the filename (without path) for cleaner display in UI.
        """
        if obj.chitti_file:
            return obj.chitti_file.name.split('/')[-1]
        return None


class ShipmentSerializer(serializers.ModelSerializer):
    """
    Main Serializer for Shipment model.
    Provides a comprehensive API representation of shipment data.
    Nested 'yatayats' are included as read-only fields.
    """
    yatayats = ShipmentYatayatSerializer(many=True, read_only=True)

    class Meta:
        model = Shipment
        fields = [
            'id',
            'invoice_no',
            'applicant',
            'vanshar',
            'bank_name',
            'bank_ref_no',
            'amount',
            'currency',
            'price_terms',
            'payment_terms',
            'insurance_company',
            'pp_no',
            'dispatch_date',
            'doc_received_date',
            'eta_date',
            'settlement_date',
            'customs_entry_date',
            'doc_to_bank',
            'yatayats',
        ]

    def to_representation(self, instance):
        """
        Customizes the serialized output to ensure consistency in empty values.
        Replaces None or empty strings with 'N/A' or 'Pending' based on context.
        """
        data = super().to_representation(instance)
        
        # Fields that should return 'N/A' or specific placeholders if empty
        optional_fields = [
            'vanshar', 'bank_name', 'bank_ref_no', 'insurance_company',
            'price_terms', 'payment_terms', 'pp_no', 'currency',
            'doc_received_date', 'eta_date', 'settlement_date', 
            'customs_entry_date', 'doc_to_bank'
        ]
        
        for field in optional_fields:
            if data.get(field) is None or data.get(field) == "":
                if field == 'settlement_date':
                    data[field] = "Pending"
                else:
                    data[field] = "N/A"
                
        return data
