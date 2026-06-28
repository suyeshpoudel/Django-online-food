from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
import uuid
# Create your models here.


class BaseModel(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# class ItemCategory(BaseModel):
#     category_name = models.CharField(max_length=100)

#     def __str__(self):
#         return self.category_name

class Item(BaseModel):
    # category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    item_name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, default='')
    price = models.IntegerField(default=100)
    image = models.ImageField(upload_to='item')

    def __str__(self):
        return self.item_name


class Cart(BaseModel):
    user = models.ForeignKey(User,null=True, blank=True, on_delete=models.SET_NULL, related_name='carts')
    is_paid = models.BooleanField(default=False)

    def get_cart_total(self):
        return CartItems.objects.filter(cart = self).aggregate(total= Sum(models.F('quantity')*models.F('item__price')))['total']

class CartItems(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_item')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_cost(self):
        return self.quantity * self.item.price
    
STATUS_CHOICES = (
    ('Accepted', 'Accepted'),
    ('Packed', 'Packed'),
    ('On the way', 'On the way'),
    ('Delivered', 'Delivered'),
    ('Cancel', 'Cancel'),
)
    
class OrderPlaced(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices= STATUS_CHOICES, max_length= 50, default='Pending')    

    @property
    def get_order_total(self):
        return self.quantity * self.item.price