from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post
import requests
from math import radians, cos, sin, sqrt, atan2
from geopy.geocoders import Nominatim
from django.shortcuts import render
from .models import Hospital
from .forms import HospitalForm
from django.contrib.admin.views.decorators import staff_member_required

# Function to calculate distance between two points using Haversine formula
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radius of Earth in kilometers
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


# Function to get latitude and longitude from an address
def get_user_location(address=""):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    return None, None


# Function to search for nearby hospitals using Overpass API (OpenStreetMap)
def find_nearby_hospitals(lat, lon, radius=5000):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:{radius},{lat},{lon});
      way["amenity"="hospital"](around:{radius},{lat},{lon});
      relation["amenity"="hospital"](around:{radius},{lat},{lon});
    );
    out center;
    """
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()

    hospitals = []
    for hospital in data['elements']:
        if 'lat' in hospital and 'lon' in hospital:
            dist = calculate_distance(lat, lon, hospital['lat'], hospital['lon'])
            hospitals.append({
                'name': hospital.get('tags', {}).get('name', 'Unknown Hospital'),
                'lat': hospital['lat'],
                'lon': hospital['lon'],
                'distance': dist,
                'beds_available': hospital.get('tags', {}).get('beds_available', 'Unknown'),
                'beds_total': hospital.get('tags', {}).get('beds', 'Unknown'),
            })

    hospitals = sorted(hospitals, key=lambda x: x['distance'])
    return hospitals


# Page 1 view where hospital search will be displayed
@login_required
def page1(request):
    hospitals = []
    user_location = None
    radius = 5  # Default radius in km

    if request.method == 'POST':
        radius = float(request.POST.get('radius', 5))
        lat = request.POST.get('latitude')
        lon = request.POST.get('longitude')

        if lat and lon:
            lat, lon = float(lat), float(lon)
            user_location = (lat, lon)
            hospitals = find_nearby_hospitals(lat, lon, radius * 1000)  # Convert km to meters

    context = {
        'hospitals': hospitals,
        'radius': radius,
        'user_location': user_location,
    }

    return render(request, 'posts/page1.html', context)


def home(request):
    posts = Post.objects.all()
    return render(request, 'posts/home.html', {'posts': posts})

def search(request):
    query = request.GET.get('q')
    results = Post.objects.filter(title__icontains=query)
    return render(request, 'posts/search_results.html', {'results': results})


@login_required
def profile(request):
    return render(request, 'posts/profile.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'posts/register.html', {'form': form})


# Login functionality
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'posts/login.html', {'form': form})

@staff_member_required
def hospital_details(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)

    if request.method == 'POST':
        form = HospitalForm(request.POST, instance=hospital)
        if form.is_valid():
            form.save()
            return redirect('hospital_details', hospital_id=hospital_id)
    else:
        form = HospitalForm(instance=hospital)

    return render(request, 'posts/hospital_details.html', {
        'hospital': hospital,
        'form': form,
    })

def page2(request):
    return render(request, 'posts/page2.html')

def page3(request):
    return render(request, 'posts/page3.html')

def page4(request):
    return render(request, 'posts/page4.html')
