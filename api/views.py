
from rest_framework.generics import *
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from api.permissions import *
from rest_framework.authentication import TokenAuthentication
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
    authentication_classes=[TokenAuthentication]
    permission_classes = [AdminPermission, IsOwner]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.id)

    def get_queryset(self):
        user = self.request.user
        return BikeParkZone.objects.filter(owner=user)




class CarParkZoneViewSet(viewsets.ModelViewSet):
    queryset = CarParkZone.objects.all()
    serializer_class = CarParkZoneSerializer
    authentication_classes=[TokenAuthentication]
    permission_classes = [AdminPermission, IsOwner]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.id)

    def get_queryset(self):
        user = self.request.user
        return CarParkZone.objects.filter(owner=user)





class HeavyParkZoneViewSet(viewsets.ModelViewSet):
    queryset = HeavyParkZone.objects.all()
    serializer_class = HeavyParkZoneSerializer
    authentication_classes=[TokenAuthentication]
    permission_classes = [AdminPermission, IsOwner]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.id)

    def get_queryset(self):
        user = self.request.user
        return HeavyParkZone.objects.filter(owner=user)
