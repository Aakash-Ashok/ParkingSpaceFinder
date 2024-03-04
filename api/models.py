from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

# Create your models here.


class customDateField(models.DateField):
    def to_python(self, value):
        if isinstance(value, str):
            return datetime.strptime(value, '%d-%m-%Y').date()
        return super().to_python(value)


class User(AbstractUser):
    dob = models.CharField(max_length=20)
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("prefer_not_to_say", "Prefer not to say"),
    ]
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default="prefer_not_to_say")
    address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    profile_image = models.ImageField(upload_to='images/profile', default='images/profile/default.jpg', blank=True, null=True)

    def formatted_dob(self):
        return self.dob.strftime('%d-%m-%Y')



class BikeParkZone(models.Model):
    name = models.CharField(
        max_length=100
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    total_slots = models.PositiveIntegerField()

    vacant_slots = models.PositiveIntegerField(
        default=0
    )

    occupied_slots = models.PositiveIntegerField(
        default=0
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    location = models.CharField(
        max_length=100
    )


class CarParkZone(models.Model):
    name = models.CharField(
        max_length=100
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    total_slots = models.PositiveIntegerField()

    vacant_slots = models.PositiveIntegerField(
        default=0
    )

    occupied_slots = models.PositiveIntegerField(
        default=0
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    location = models.CharField(
        max_length=100
    )


class HeavyParkZone(models.Model):
    name = models.CharField(
        max_length=100
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    total_slots = models.PositiveIntegerField()

    vacant_slots = models.PositiveIntegerField(
        default=0
    )

    occupied_slots = models.PositiveIntegerField(
        default=0
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    location = models.CharField(
        max_length=100
    )


class BikeReservation(models.Model):
    ticket_code = models.CharField(max_length=6, blank=True, null=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    finish_time = models.DateTimeField()
    parking_zone = models.ForeignKey(BikeParkZone, on_delete=models.CASCADE)
    plate_number = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=16)
    checked_out = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return f'Reservation for vehicle: {self.plate_number}'


class CarReservation(models.Model):
    ticket_code = models.CharField(max_length=6, blank=True, null=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.TimeField()
    finish_time = models.TimeField()
    parking_zone = models.ForeignKey(CarParkZone, on_delete=models.CASCADE)
    plate_number = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=16)
    checked_out = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return f'Reservation for vehicle: {self.plate_number}'


class HeavyReservation(models.Model):
    ticket_code = models.CharField(max_length=6, blank=True, null=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.TimeField()
    finish_time = models.TimeField()
    parking_zone = models.ForeignKey(CarParkZone, on_delete=models.CASCADE)
    plate_number = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=16)
    checked_out = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return f'Reservation for vehicle: {self.plate_number}'
