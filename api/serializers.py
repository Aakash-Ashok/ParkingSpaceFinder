from rest_framework import serializers
from datetime import datetime
from api.models import *
from django.core.validators import RegexValidator

class CustomDateFormatField(serializers.DateField):
    def to_internal_value(self, value):
        try:
            date_object = datetime.strptime(value, '%d-%m-%Y').date()
            return date_object
        except ValueError:
            self.fail('invalid')

class AdminSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name","last_name","email","username","password","dob","gender","address","phone_number","profile_image","is_staff"]

    def create(self, validated_data):
        validated_data["is_staff"] = True
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name","last_name","email","username","password","dob","gender","address","phone_number","profile_image","is_staff"]

    def create(self, validated_data):
        validated_data["is_staff"] = False
        user = User.objects.create_user(**validated_data)
        return user
    

class BikeParkZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model=BikeParkZone
        exclude=["owner",]

class CarParkZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model=BikeParkZone
        exclude=["owner",]

class HeavyParkZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model=BikeParkZone
        exclude=["owner",] 


class BikeReservationSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField()
    finish_time = serializers.DateTimeField()
    parking_zone = serializers.IntegerField()
    plate_number = serializers.CharField(validators=[RegexValidator(
        regex=r'^[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}$', 
        message='Plate number must be in the format KXX123X',
        code='invalid_plate_number'
    )])

    phone_number = serializers.CharField(validators=[RegexValidator(
        regex=r'^[0-9]+$',
        message='Phone number must contain only digits',
        code='invalid_phone_number'
    )])

    class Meta:
        model = BikeReservation
        exclude = ['ticket_code', 'customer', 'checked_out']


class CarReservationSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField()
    finish_time = serializers.DateTimeField()
    parking_zone = serializers.IntegerField()
    plate_number = serializers.CharField(validators=[RegexValidator(
        regex=r'^[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}$', 
        message='Plate number must be in the format KXX123X',
        code='invalid_plate_number'
    )])

    phone_number = serializers.CharField(validators=[RegexValidator(
        regex=r'^[0-9]+$',
        message='Phone number must contain only digits',
        code='invalid_phone_number'
    )])

    class Meta:
        model = CarReservation
        exclude = ['ticket_code', 'customer', 'checked_out']

class HeavyReservationSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField()
    finish_time = serializers.DateTimeField()
    parking_zone = serializers.IntegerField()
    plate_number = serializers.CharField(validators=[RegexValidator(
        regex=r'^[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}$', 
        message='Plate number must be in the format KXX123X',
        code='invalid_plate_number'
    )])

    phone_number = serializers.CharField(validators=[RegexValidator(
        regex=r'^[0-9]+$',
        message='Phone number must contain only digits',
        code='invalid_phone_number'
    )])

    class Meta:
        model = HeavyReservation
        exclude = ['ticket_code', 'customer', 'checked_out']