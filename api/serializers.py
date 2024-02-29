from rest_framework import serializers
from datetime import datetime
from api.models import *
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate

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