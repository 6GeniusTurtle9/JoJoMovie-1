from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from django.contrib.auth import get_user_model
from movies.models import Rating, Movie

# Create your views here.
def signup(request):
    if request.user.is_authenticated:
        return redirect('movies:index')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('movies:index')
    else:
        form = CustomUserCreationForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/login_signup.html', context)

def login(request):
    if request.user.is_authenticated:
        return redirect('movies:index')
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('movies:index')
    else:
        form = AuthenticationForm()
    context = {
        'form' : form
    }
    return render(request, 'accounts/login_signup.html', context)

@login_required
def logout(request):
    auth_logout(request)
    return redirect('movies:index')

@login_required
def profile(request, pk):
    User = get_user_model()
    user = get_object_or_404(User, pk=pk)
    user_ratings = Rating.objects.filter(user=user)
    genres_dict = {}
    genres_count = {}
    for user_rating in user_ratings:
        user_genres = user_rating.movie.genres.all()
        for user_genre in user_rating.movie.genres.all():
            print(user_genre.name, user_rating.point)
            if user_genre.name in genres_dict:
                genres_dict[user_genre.name] += user_rating.point
                genres_count[user_genre.name] += 1
            else:
                genres_dict[user_genre.name] = user_rating.point
                genres_count[user_genre.name] = 1
    
    
    for key in genres_count:
        genres_dict[key] /= genres_count[key]
    genres_sort = sorted(genres_dict.items(), key=lambda x:x[1], reverse=True)

    most_liked_genre = genres_sort[0][0]
    recommend_movies = []
    for movie in Movie.objects.order_by('-popularity'):
        for genre in movie.genres.all():
            if most_liked_genre == genre.name:
                recommend_movies.append(movie)
                print(movie.title, genre.name)
                break
        print(len(recommend_movies))
        if len(recommend_movies) > 10:
            break
    print(recommend_movies)
    print(genres_sort[0])
    print(genres_dict)
    context = {
        'user': user,
        'user_ratings': user_ratings,
        'recommend_movies': recommend_movies,
    }
    return render(request, 'accounts/profile.html', context)