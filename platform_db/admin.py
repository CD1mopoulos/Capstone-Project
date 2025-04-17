from django.contrib import admin
from .models import DeliveryOrder
from .models import (
    CustomUser,
    UserDetails,
    Restaurant,
    Dish,
    RestReview,
    OrderItem,
    Purchase,
    PurchasedDish,
    GeneralComment,
)

# Register your models here
admin.site.register(CustomUser)
admin.site.register(UserDetails)
admin.site.register(Restaurant)
admin.site.register(Dish)
admin.site.register(RestReview)
admin.site.register(OrderItem)
admin.site.register(Purchase)
admin.site.register(PurchasedDish)
admin.site.register(GeneralComment)

@admin.register(DeliveryOrder)
class DeliveryOrderAdmin(admin.ModelAdmin):
    list_display = ('purchase', 'delivery', 'status', 'assigned_at')
    list_filter = ('status', 'delivery')
