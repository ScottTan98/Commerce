from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, category, listing, bid, comment


def index(request):
    activeListing = listing.objects.filter(isActive=True)
    allcategories = category.objects.all()
    return render(request, "auctions/index.html", {
        "listings":activeListing,
        "category":allcategories
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create(request):
    if request.method=="GET":
        allcategories = category.objects.all()
        return render(request, "auctions/create.html",{
            "category":allcategories
         })
    else:
        title = request.POST["title"]
        description = request.POST["description"]
        url = request.POST["url"]
        price = request.POST["price"]
        Inputcategory = request.POST["category"]

        categoryData = category.objects.get(categoryName=Inputcategory)

        currentUser = request.user  

        bidPrice = bid(bidingPrice=float(price), user=currentUser)
        bidPrice.save()

        alllist= listing(
            title=title, 
            description=description, 
            url=url, 
            price=bidPrice, 
            category=categoryData, 
            owner=currentUser)
        alllist.save()

        return HttpResponseRedirect(reverse("index"))

def filterPage(request):
    if request.method=="POST":
        filterInput = request.POST["category"]
        categoryData = category.objects.get(categoryName=filterInput)
        activeListing = listing.objects.filter(isActive=True, category=categoryData)
        allcategories = category.objects.all()
        return render(request, "auctions/index.html", {
            "listings":activeListing,
            "category":allcategories
        })

def listingPage(request, id):
    listingData = listing.objects.get(pk=id)
    listingWatchlist = request.user in listingData.watchlist.all()
    allComment = comment.objects.filter(listing=listingData)
    isOwner = request.user.username == listingData.owner.username
    return render(request, "auctions/listing.html", {
        "list": listingData,
        "listingWatchlist": listingWatchlist,
        "message": allComment,
        "isOwner": isOwner,
        "closeComment": "Your Auction is closed!"
    })

def removeWatchlist(request,id):
    listingData = listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listingPage", args=(id,)))

def addWatchlist(request,id):
    listingData = listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listingPage", args=(id,)))

def watchlist(request):
    currentuser = request.user
    listingData = currentuser.watchlistUser.all()
    return render(request, "auctions/watchlist.html", {
        "listData" : listingData
    })

def addComment(request,id):
    currentuser = request.user
    listingData = listing.objects.get(pk=id)
    newComment = request.POST["newComment"]

    addNewComment = comment(
        author=currentuser,
        listing=listingData,
        message=newComment 
    )
    addNewComment.save()
    
    return HttpResponseRedirect(reverse("listingPage", args=(id,)))

def addBid(request,id):
    currentuser = request.user
    newbid = float(request.POST["bid_price"])
    listingData = listing.objects.get(pk=id)
    oldbid = listingData.price.bidingPrice
    listingWatchlist = request.user in listingData.watchlist.all()
    allComment = comment.objects.filter(listing=listingData)
    isOwner = request.user.username == listingData.owner.username
    if newbid > oldbid:
        updatebid = bid(bidingPrice=newbid, user=currentuser)
        updatebid.save()
        listingData.price = updatebid
        listingData.save()
        return render(request, "auctions/listing.html", {
            "list": listingData,
            "listingWatchlist": listingWatchlist,
            "message": allComment,
            "bidComment" : "Bid Successfully!",
            "status" : True,
            "isOwner": isOwner,
            "closeComment": "Your Auction is closed!"
        })

    else:
        return render(request, "auctions/listing.html", {
            "list": listingData,
            "listingWatchlist": listingWatchlist,
            "message": allComment,
            "bidComment" : "Bid amount must more than current amount!",
            "status" : False,
            "isOwner": isOwner,
            "closeComment": "Your Auction is closed!"
        })
    
def removeAuction(request,id):
    listingData = listing.objects.get(pk=id)
    listingData.isActive = False
    listingData.save()

    listingWatchlist = request.user in listingData.watchlist.all()
    allComment = comment.objects.filter(listing=listingData)
    isOwner = request.user.username == listingData.owner.username
    return render(request, "auctions/listing.html", {
        "list": listingData,
        "listingWatchlist": listingWatchlist,
        "message": allComment,
        "isOwner": isOwner,
        "status" : True,
        "closeComment": "Your Auction is closed!"
    })