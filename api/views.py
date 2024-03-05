
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
    

class BikeParkZoneViewSet(viewsets.ModelViewSet):
    queryset = BikeParkZone.objects.all()
    serializer_class = BikeParkZoneSerializer
    authentication_classes = [BasicAuthentication,TokenAuthentication]
    permission_classes = [AdminPermission, IsOwner,permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        return BikeParkZone.objects.filter(owner=user)

    # @action(detail=True, methods=['get'])
    # def custom_action(self, request, pk=None):
    #     return Response({'message': 'Custom action executed'})


class CarParkZoneViewSet(viewsets.ModelViewSet):
    queryset = CarParkZone.objects.all()
    serializer_class = CarParkZoneSerializer
    authentication_classes=[TokenAuthentication,BasicAuthentication]
    permission_classes = [AdminPermission, IsOwner,permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        return CarParkZone.objects.filter(owner=user)


class HeavyParkZoneViewSet(viewsets.ModelViewSet):
    queryset = HeavyParkZone.objects.all()
    serializer_class = HeavyParkZoneSerializer
    authentication_classes=[TokenAuthentication,BasicAuthentication]
    permission_classes = [AdminPermission, IsOwner,permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        return HeavyParkZone.objects.filter(owner=user)


def create_ticket_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))


class BaseReservationView(APIView):
    authentication_classes = [BasicAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    model = None
    serializer_class = None
    park_zone_model = None

    def get(self, request):
        try:
            user_reservation = self.model.objects.get(customer=request.user, checked_out=False)
            serializer = self.serializer_class(user_reservation)
            return Response(serializer.data)
        except self.model.DoesNotExist:
            return Response({'message': 'No active reservation found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        try:
            user_reservation = self.model.objects.get(customer=request.user, checked_out=False)
            return Response({'message': 'Please Check Out Your Previous Reservation'}, status=status.HTTP_400_BAD_REQUEST)
        except self.model.DoesNotExist:
            pass

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            start_time = serializer.validated_data['start_time']
            end_time = serializer.validated_data['finish_time']
            parking_zone_id = serializer.validated_data['parking_zone']

            if start_time >= end_time:
                return Response({'message': 'End time must be after start time'}, status=status.HTTP_400_BAD_REQUEST)

            parking_zone = get_object_or_404(self.park_zone_model, id=parking_zone_id)
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


class BikeReservationView(BaseReservationView):
    model = BikeReservation
    serializer_class = BikeReservationSerializer
    park_zone_model = BikeParkZone


class CarReservationView(BaseReservationView):
    model = CarReservation
    serializer_class = CarReservationSerializer
    park_zone_model = CarParkZone


class HeavyReservationView(BaseReservationView):
    model = HeavyReservation
    serializer_class = HeavyReservationSerializer
    park_zone_model = HeavyParkZone


class BikeParkingZoneSearchView(APIView):
    authentication_classes = [BasicAuthentication,TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    def get(self, request):
        location = request.GET.get('location')
        if location:
            zones = BikeParkZone.objects.filter(location__icontains=location)
        else:
            zones = BikeParkZone.objects.all()

        serializer = BikeParkZoneSerializer(zones, many=True)
        return Response(serializer.data)


class CarParkingZoneSearchView(APIView):
    authentication_classes = [BasicAuthentication,TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    def get(self, request):
        location = request.GET.get('location')
        if location:
            zones = CarParkZone.objects.filter(location__icontains=location)
        else:
            zones = CarParkZone.objects.all()

        serializer = CarParkZoneSerializer(zones, many=True)
        return Response(serializer.data)
    

class HeavyParkingZoneSearchView(APIView):
    authentication_classes = [BasicAuthentication,TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    def get(self, request):
        location = request.GET.get('location')
        if location:
            zones = HeavyParkZone.objects.filter(location__icontains=location)
        else:
            zones = HeavyParkZone.objects.all()

        serializer = HeavyParkZoneSerializer(zones, many=True)
        return Response(serializer.data)


class BikeTicketPdfView(APIView):
    authentication_classes = [BasicAuthentication,TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.now()
        reservation = BikeReservation.objects.filter(Q(customer=request.user, checked_out=False) | Q(customer=request.user, checked_out=True)).first()
        if reservation:
            data = {
                'today': today,
                'reservation': reservation.id  # Assuming you want to return the ID of the reservation
            }
            return Response(data)
        else:
            messages.warning(request, f'No Parking reservation exists for {request.user}')
            return Response({'message': f'No Parking reservation exists for {request.user}'}, status=status.HTTP_404_NOT_FOUND)
        

class CarTicketPdfView(APIView):
    authentication_classes = [BasicAuthentication,TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.now()
        reservation = CarReservation.objects.filter(Q(customer=request.user, checked_out=False) | Q(customer=request.user, checked_out=True)).first()
        if reservation:
            data = {
                'today': today,
                'reservation': reservation.id  # Assuming you want to return the ID of the reservation
            }
            return Response(data)
        else:
            messages.warning(request, f'No Parking reservation exists for {request.user}')
            return Response({'message': f'No Parking reservation exists for {request.user}'}, status=status.HTTP_404_NOT_FOUND)
        

class HeavyTicketPdfView(APIView):
    authentication_classes = [BasicAuthentication,TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.now()
        reservation = HeavyReservation.objects.filter(Q(customer=request.user, checked_out=False) | Q(customer=request.user, checked_out=True)).first()
        if reservation:
            data = {
                'today': today,
                'reservation': reservation.id  # Assuming you want to return the ID of the reservation
            }
            return Response(data)
        else:
            messages.warning(request, f'No Parking reservation exists for {request.user}')
            return Response({'message': f'No Parking reservation exists for {request.user}'}, status=status.HTTP_404_NOT_FOUND)
        


class BikeCheckOutView(APIView):
    authentication_classes = [BasicAuthentication,TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    def post(self, request):
        try:
            reservation = BikeReservation.objects.filter(customer=request.user, checked_out=False).first()
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
        

class CarCheckOutView(APIView):
    authentication_classes = [BasicAuthentication,TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    def post(self, request):
        try:
            reservation = CarReservation.objects.filter(customer=request.user, checked_out=False).first()
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
        

class HeavyCheckOutView(APIView):
    authentication_classes = [BasicAuthentication,TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    def post(self, request):
        try:
            reservation = HeavyReservation.objects.filter(customer=request.user, checked_out=False).first()
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