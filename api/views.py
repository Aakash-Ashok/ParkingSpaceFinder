
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
from datetime import timedelta
from django.db import transaction
from django.shortcuts import get_object_or_404
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
        serializer.save(owner=self.request.user.id)

    def get_queryset(self):
        user = self.request.user
        return CarParkZone.objects.filter(owner=user)


class HeavyParkZoneViewSet(viewsets.ModelViewSet):
    queryset = HeavyParkZone.objects.all()
    serializer_class = HeavyParkZoneSerializer
    authentication_classes=[TokenAuthentication,BasicAuthentication]
    permission_classes = [AdminPermission, IsOwner,permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.id)

    def get_queryset(self):
        user = self.request.user
        return HeavyParkZone.objects.filter(owner=user)


def create_ticket_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))


class BikeReservationView(APIView):
    authentication_classes = [BasicAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            user_reservation = BikeReservation.objects.get(customer=request.user, checked_out=False)
            serializer = BikeReservationSerializer(user_reservation)
            return Response(serializer.data)
        except BikeReservation.DoesNotExist:
            return Response({'message': 'No active reservation found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        try:
            user_reservation = BikeReservation.objects.get(customer=request.user, checked_out=False)
            return Response({'message': 'Please Check Out Your Previous Reservation'}, status=status.HTTP_400_BAD_REQUEST)
        except BikeReservation.DoesNotExist:
            pass

        serializer = BikeReservationSerializer(data=request.data)
        if serializer.is_valid():
            start_time = serializer.validated_data['start_time']
            end_time = serializer.validated_data['finish_time']
            parking_zone_id = serializer.validated_data['parking_zone']

            if start_time >= end_time:
                return Response({'message': 'End time must be after start time'}, status=status.HTTP_400_BAD_REQUEST)

            parking_zone = get_object_or_404(BikeParkZone, id=parking_zone_id)
            if parking_zone.vacant_slots == 0:
                return Response({'message': 'Parking Zone Full!'}, status=status.HTTP_400_BAD_REQUEST)

            ticket_code = create_ticket_code()
            while BikeReservation.objects.filter(ticket_code=ticket_code).exists():
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
            user_reservation = BikeReservation.objects.get(customer=request.user, checked_out=False)
            user_reservation.delete()
            return Response({'message': 'Reservation deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except BikeReservation.DoesNotExist:
            return Response({'message': 'No active reservation found'}, status=status.HTTP_404_NOT_FOUND)
        

class CarReservationView(APIView):
    authentication_classes = [BasicAuthentication,TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    def get(self, request):
        try:
            user_reservation = CarReservation.objects.get(customer=request.user, checked_out=False)
            serializer = CarReservationSerializer(user_reservation)
            return Response(serializer.data)
        except CarReservation.DoesNotExist:
            return Response({'message': 'No active reservation found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        try:
            user_reservation = CarReservation.objects.get(customer=request.user, checked_out=False)
            return Response({'message': 'Please Check Out Your Previous Reservation'}, status=status.HTTP_400_BAD_REQUEST)
        except CarReservation.DoesNotExist:
            pass

        serializer = CarReservationSerializer(data=request.data)
        if serializer.is_valid():
            start_time = serializer.validated_data['start_time']
            end_time = serializer.validated_data['finish_time']
            parking_zone = serializer.validated_data['parking_zone']

            if start_time >= end_time:
                return Response({'message': 'End time must be after start time'}, status=status.HTTP_400_BAD_REQUEST)

            parkingzone = get_object_or_404(CarParkZone, id=parking_zone)
            if parkingzone.vacant_slots == 0:
                return Response({'message': 'Parking Zone Full!'}, status=status.HTTP_400_BAD_REQUEST)

            ticket_code = create_ticket_code()
            while CarReservation.objects.filter(ticket_code=ticket_code).exists():
                ticket_code = create_ticket_code()

            reservation = serializer.save(customer=request.user, parking_zone=parkingzone, ticket_code=ticket_code)
            parkingzone.occupied_slots += 1
            parkingzone.vacant_slots = parkingzone.total_slots - parkingzone.occupied_slots
            parkingzone.save()

            return Response({'message': 'Successfully Booked'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        try:
            user_reservation = CarReservation.objects.get(customer=request.user, checked_out=False)
            user_reservation.delete()
            return Response({'message': 'Reservation deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except CarReservation.DoesNotExist:
            return Response({'message': 'No active reservation found'}, status=status.HTTP_404_NOT_FOUND)


class HeavyReservationView(APIView):
    authentication_classes = [BasicAuthentication,TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    def get(self, request):
        try:
            user_reservation = HeavyReservation.objects.get(customer=request.user, checked_out=False)
            serializer = HeavyReservationSerializer(user_reservation)
            return Response(serializer.data)
        except HeavyReservation.DoesNotExist:
            return Response({'message': 'No active reservation found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        try:
            user_reservation = HeavyReservation.objects.get(customer=request.user, checked_out=False)
            return Response({'message': 'Please Check Out Your Previous Reservation'}, status=status.HTTP_400_BAD_REQUEST)
        except HeavyReservation.DoesNotExist:
            pass

        serializer = HeavyReservationSerializer(data=request.data)
        if serializer.is_valid():
            start_time = serializer.validated_data['start_time']
            end_time = serializer.validated_data['finish_time']
            parking_zone = serializer.validated_data['parking_zone']

            if start_time >= end_time:
                return Response({'message': 'End time must be after start time'}, status=status.HTTP_400_BAD_REQUEST)

            parkingzone = get_object_or_404(HeavyParkZone, id=parking_zone)
            if parkingzone.vacant_slots == 0:
                return Response({'message': 'Parking Zone Full!'}, status=status.HTTP_400_BAD_REQUEST)

            ticket_code = create_ticket_code()
            while HeavyReservation.objects.filter(ticket_code=ticket_code).exists():
                ticket_code = create_ticket_code()

            reservation = serializer.save(customer=request.user, parking_zone=parkingzone, ticket_code=ticket_code)
            parkingzone.occupied_slots += 1
            parkingzone.vacant_slots = parkingzone.total_slots - parkingzone.occupied_slots
            parkingzone.save()

            return Response({'message': 'Successfully Booked'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        try:
            user_reservation = HeavyReservation.objects.get(customer=request.user, checked_out=False)
            user_reservation.delete()
            return Response({'message': 'Reservation deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except HeavyReservation.DoesNotExist:
            return Response({'message': 'No active reservation found'}, status=status.HTTP_404_NOT_FOUND)



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
