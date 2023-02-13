from email.policy import default
from pickle import TRUE
from unittest.util import _MAX_LENGTH
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class category(models.Model):
    categoryName = models.CharField(max_length=40)

    def __str__(self):
        return self.categoryName

class bid(models.Model):
    bidingPrice = models.FloatField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="userBid")
    
    def __str__(self):
        return f"{self.user} Bidding Price = {self.bidingPrice}"

class listing(models.Model):
    title = models.CharField(max_length=40)
    description = models.CharField(max_length=400)
    url = models.CharField(max_length=2000)
    price = models.ForeignKey(bid, on_delete=models.CASCADE, blank=True, null=True, related_name="bid")
    isActive = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
    category = models.ForeignKey(category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    watchlist = models.ManyToManyField(User, blank=True, null=True, related_name="watchlistUser")

    def __str__(self):
        return self.title

class comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="commentUser")
    listing = models.ForeignKey(listing, on_delete=models.CASCADE, blank=True, null=True, related_name="listingComment")
    message = models.CharField(max_length=200, null=TRUE)

    def __str__(self):
        return f"{self.author} comment on {self.listing}"        
