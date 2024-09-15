from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    link = models.URLField()

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    products = models.ManyToManyField(Product)
    combined_image = models.ImageField(upload_to='posts/')

    def __str__(self):
        return self.title


class Hospital(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    beds_total = models.IntegerField(default=0)
    beds_available = models.IntegerField(default=0)

    def __str__(self):
        return self.name