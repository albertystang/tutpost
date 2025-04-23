from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.http import Http404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.db.models import Count
from .forms import *
from a_posts.forms import ReplyCreateForm


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You are logged in successfully...')
            return redirect('home')
        else:
            messages.success(request, 'There was an error logging in. Pleae try again...')
            return redirect('login')
    return render(request, 'a_users/login.html')


def logout_user(request):
    logout(request)
    messages.success(request, "You have successfully logged out,. Bye!...")
    return redirect('home')


def signup_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']            
            # Log in user
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "You have successfully signed up! Please complete your profile before proceeding...")          
                return redirect('profile-onboarding')    
    return render(request, 'a_users/signup.html', {'form': form})


def profile_view(request, username=None):
    if username:
        profile = get_object_or_404(User, username=username).profile
    else:
        try:        
            profile = request.user.profile
        except:
            raise Http404()
    posts = profile.user.posts.all()

    if request.htmx:
        if 'top-posts' in request.GET:
            posts = profile.user.posts.annotate(num_likes=Count('likes')).filter(num_likes__gt=0).order_by('-num_likes')            
        elif 'top-comments' in request.GET:
            comments = profile.user.comments.annotate(num_likes=Count('likes')).filter(num_likes__gt=0).order_by('-num_likes')
            replyform = ReplyCreateForm()
            return render(request, 'snippets/loop_profile_comments.html', {'comments': comments, 'replyform': replyform})
        elif 'liked-posts' in request.GET:
            posts = profile.user.likedposts.order_by('-likedpost__created')       
        return render(request, 'snippets/loop_profile_posts.html', {'posts': posts})
    
    context = {
        'profile': profile,
        'posts': posts
    }
    return render(request, 'a_users/profile.html', context)


@login_required
def profile_edit_view(request):
    form = ProfileForm(instance=request.user.profile)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile) 
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated...')
            return redirect('profile')          
    return render(request, 'a_users/profile_edit.html', {'form': form})


@login_required
def profile_onboarding_view(request):
    form = ProfileForm(instance=request.user.profile)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile) 
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated...')
            return redirect('profile')        
    return render(request, 'a_users/profile_onboarding.html', {'form': form})


@login_required
def profile_delete_view(request):
    user = request.user
    if request.method == 'POST':
        logout(request)
        user.delete()
        messages.success(request, 'Account deleted. What a pity!')
        return redirect('home')
    return render(request, 'a_users/profile_delete.html')