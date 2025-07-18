from django.db import models

# Create your models here.


from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    

    def average_rating(self):
        return self.reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
    
    def __str__(self):
        return self.name
    
    
    
    
class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    feedback = models.TextField()

    class Meta:
        unique_together = ('product', 'user')