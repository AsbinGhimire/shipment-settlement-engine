from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .models import Shipment
from .serializers import ShipmentSerializer


class LoginAPIView(APIView):
    """
    API View for user login.
    Returns an Auth Token for valid credentials.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {"error": "Please provide both username and password"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST
            )

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff
        })


class ShipmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing Shipments.
    Provides `list` and `retrieve` actions.
    Authentication is required.
    """
    queryset = Shipment.objects.all().order_by('-dispatch_date', '-id')
    serializer_class = ShipmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optionally restrict the returned shipments by filtering.
        """
        queryset = super().get_queryset()
        # Example: Filter by applicant if needed
        applicant = self.request.query_params.get('applicant')
        if applicant:
            queryset = queryset.filter(applicant__icontains=applicant)
        return queryset