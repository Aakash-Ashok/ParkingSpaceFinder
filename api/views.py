
from rest_framework.generics import *
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from api.permissions import *
from rest_framework.authentication import TokenAuthentication,BasicAuthentication
import random
import string
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.

class UserRegistration(APIView):
    def post(self, request):
        serializer = UserSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AdminRegistration(APIView):
    def post(self, request, format=None):
        serializer = AdminSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ParkZoneViewSet(viewsets.ModelViewSet):
    queryset = ParkZone.objects.all()
    serializer_class = ParkZoneSerializer
    authentication_classes = [BasicAuthentication, TokenAuthentication]
    permission_classes = [AdminPermission, IsOwner, permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        return ParkZone.objects.filter(owner=user)

    def create(self, request, *args, **kwargs):
        vehicle_type = request.data.get('vehicle_type')
        if vehicle_type not in ['bike', 'car', 'heavy']:
            return Response({"detail": "Invalid vehicle type"}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        vehicle_type = request.data.get('vehicle_type')
        if vehicle_type not in ['bike', 'car', 'heavy']:
            return Response({"detail": "Invalid vehicle type"}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

def create_ticket_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))


class ReservationView(APIView):
    authentication_classes = [BasicAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    model = Reservation
    serializer_class = ReservationSerializer

    def get(self, request):
        try:
            user_reservation = self.model.objects.filter(customer=request.user, checked_out=False).first()
            if user_reservation:
                serializer = self.serializer_class(user_reservation)
                return Response(serializer.data)
            else:
                return Response({'message': 'No active reservation found'}, status=status.HTTP_404_NOT_FOUND)
        except self.model.DoesNotExist:
            return Response({'message': 'No active reservation found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            start_time = serializer.validated_data['start_time']
            end_time = serializer.validated_data['finish_time']
            parking_zone_id = serializer.validated_data['parking_zone']
            vehicle_type = serializer.validated_data.get('vehicle_type')

            if start_time >= end_time:
                return Response({'message': 'End time must be after start time'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if there is an active reservation for the same vehicle type
            active_reservations = self.model.objects.filter(customer=request.user, checked_out=False, parking_zone__vehicle_type=vehicle_type)
            if active_reservations.exists():
                return Response({'message': 'You already have an active reservation for this vehicle type'}, status=status.HTTP_400_BAD_REQUEST)

            parking_zone = get_object_or_404(ParkZone, id=parking_zone_id)
            if parking_zone.vacant_slots == 0:
                return Response({'message': 'Parking Zone Full!'}, status=status.HTTP_400_BAD_REQUEST)

            ticket_code = create_ticket_code()
            while self.model.objects.filter(ticket_code=ticket_code).exists():
                ticket_code = create_ticket_code()

            total_hours = (end_time - start_time).total_seconds() / 3600
            total_price = total_hours * float(parking_zone.price)

            with transaction.atomic():
                reservation = serializer.save(customer=request.user, parking_zone=parking_zone, ticket_code=ticket_code, total_price=total_price)
                parking_zone.occupied_slots += 1
                parking_zone.vacant_slots = parking_zone.total_slots - parking_zone.occupied_slots
                parking_zone.save()

            return Response({'message': 'Successfully Booked', 'total_price': total_price}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request):
        try:
            user_reservation = self.model.objects.get(customer=request.user, checked_out=False)
            with transaction.atomic():
                parking_zone = user_reservation.parking_zone
                parking_zone.occupied_slots -= 1
                parking_zone.vacant_slots += 1
                parking_zone.save()
                user_reservation.delete()
            return Response({'message': 'Reservation deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except self.model.DoesNotExist:
            return Response({'message': 'No active reservation found'}, status=status.HTTP_404_NOT_FOUND)
        
class ParkingZoneSearchView(APIView):
    authentication_classes = [BasicAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        location = request.data.get('location')
        vehicle_type = request.data.get('vehicle_type')

        if location and vehicle_type:
            zones = ParkZone.objects.filter(location__icontains=location, vehicle_type__iexact=vehicle_type)
        elif location:
            zones = ParkZone.objects.filter(location__icontains=location)
        elif vehicle_type:
            zones = ParkZone.objects.filter(vehicle_type__iexact=vehicle_type)
        else:
            return Response({'error': 'Please provide location and/or vehicle_type parameters.'}, status=400)

        serializer = ParkZoneSearchSerializer(zones, many=True)
        return Response(serializer.data)
    
class TicketPdfView(APIView):
    authentication_classes = [BasicAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.now()
        vehicle_type = request.GET.get('vehicle_type')
        reservations = Reservation.objects.filter(customer=request.user).filter(Q(checked_out=False) | Q(checked_out=True))
        if vehicle_type:
            reservations = reservations.filter(vehicle_type=vehicle_type)
        if reservations.exists():
            data = {
                'today': today,
                'reservations': ReservationSerializer(reservations, many=True).data
            }
            return Response(data)
        else:
            message = f'No Parking reservations exist for {request.user}'
            return Response({'message': message}, status=status.HTTP_404_NOT_FOUND)

class CheckOutView(APIView):
    authentication_classes = [BasicAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        vehicle_type = request.data.get('vehicle_type')
        if vehicle_type not in ['bike', 'car', 'heavy']:
            return Response({'message': 'Invalid vehicle type'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            reservation = Reservation.objects.filter(customer=request.user, checked_out=False, vehicle_type=vehicle_type).first()
            if reservation:
                reservation.checked_out = True
                reservation.save()

                parking_zone = reservation.parking_zone
                parking_zone.occupied_slots -= 1
                parking_zone.vacant_slots += 1
                parking_zone.save()

                return Response({'message': 'Successfully Checked Out'})
            else:
                return Response({'message': f'No Parking reservation exists for {request.user}'}, status=status.HTTP_404_NOT_FOUND)
        except ObjectDoesNotExist:
            return Response({'message': f'No Parking reservation exists for {request.user}'}, status=status.HTTP_404_NOT_FOUND)

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            if not request.user.check_password(serializer.data.get('old_password')):
                return Response({'old_password': ['Wrong password.']}, status=status.HTTP_400_BAD_REQUEST)
            request.user.set_password(serializer.data.get('new_password'))
            request.user.save()
            return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)