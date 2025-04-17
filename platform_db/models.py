from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model 
from django.contrib.auth.models import AbstractUser, Group, Permission

class CustomUser(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    is_employee = models.BooleanField(default=False)
    is_restaurant = models.BooleanField(default=False)
    is_delivery = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    # Fix related name clashes
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",  # Unique related name to avoid conflict
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",  # Unique related name to avoid conflict
        blank=True
    )

    def __str__(self):
        return self.username

class UserDetails(models.Model):
    user_del_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    surename = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Details of {self.user.username}"

class Restaurant(models.Model):
    rest_id = models.AutoField(primary_key=True)
    owner = models.OneToOneField(CustomUser, on_delete=models.CASCADE, blank=True, null=True, related_name="owned_restaurant")
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)  
    longitude = models.FloatField(blank=True, null=True)  
    rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)

    def __str__(self):
        return self.name

class Dish(models.Model):
    dish_id = models.AutoField(primary_key=True)
    restaurants = models.ManyToManyField(Restaurant, related_name="dishes")
    dish_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    ingredients = models.TextField(blank=True, null=True)
    search_tag = models.CharField(max_length=255, blank=True, null=True)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)

    def __str__(self):
        return self.dish_name
    
User = get_user_model() 

class CartItem(models.Model):
    cart_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)  
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)  
    quantity = models.PositiveIntegerField(default=1)  
    added_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.quantity} x {self.dish.dish_name} for {self.user.username}"
class RestReview(models.Model):
    review_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    rating = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.restaurant.name}"

class OrderItem(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    added_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity}x {self.dish.dish_name} for {self.user.username}"

class Purchase(models.Model):
    purch_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"Purchase {self.purch_id} by {self.user.username}"

class PurchasedDish(models.Model):
    purch_dish_id = models.AutoField(primary_key=True)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.quantity}x {self.dish.dish_name} in Purchase {self.purchase.purch_id}"

class GeneralComment(models.Model):
    gc_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True, blank=True)
    surname = models.CharField(max_length=100, null=True, blank=True)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Comment by {self.user.username}"


class DeliveryOrder(models.Model):
    delivery = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'is_delivery': True})
    purchase = models.OneToOneField('platform_db.Purchase', on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=[
        ('assigned', 'Assigned'),
        ('picked', 'Picked'),
        ('delivered', 'Delivered')
    ], default='assigned')
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Delivery of {self.purchase} by {self.delivery.username}"
