from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
import json
from django.views.decorators.csrf import csrf_protect

from django.shortcuts import render

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.utils import timezone

from socialnetwork.forms import LoginForm, RegisterForm, ProfileForm, PostForm
from socialnetwork.models import Profile, Post, Comment, FollowRelationship

@ensure_csrf_cookie
def login_action(request):
    context = {}
    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'socialnetwork/login.html', context)

    # Creates a bound form from the request POST parameters
    # And makes the form available in the request context dictionary.
    form = LoginForm(request.POST)

    # Validates the form.
    if not form.is_valid():
        context['form'] = form
        return render(request, 'socialnetwork/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect('globalStream')


@ensure_csrf_cookie
def logout_action(request):
    logout(request)
    return redirect('login')


@ensure_csrf_cookie
def register_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        # initialize a new form object (unbound form)
        context['form'] = RegisterForm()
        return render(request, 'socialnetwork/register.html', context)

    # Creates a bound form from the request POST parameters
    # and makes the form available in the request context dictionary
    form = RegisterForm(request.POST)

    # Validates the form.
    if not form.is_valid():
        # the form object has errors built into it
        context['form'] = form
        return render(request, 'socialnetwork/register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password1'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    Profile.objects.create(user = new_user)
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password1'])

    login(request, new_user)
    return redirect('globalStream')



@ensure_csrf_cookie
@login_required
def my_profile_action(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            if 'picture' in request.FILES:
                profile.content_type = request.FILES['picture'].content_type
            form.save()
            return redirect('myProfile')
    else:
        form = ProfileForm(instance=profile)

    context = {
        'profile': profile,
        'following': profile.following.all(),
        'form': form
    }
    return render(request, 'socialnetwork/myProfile.html', context)



@ensure_csrf_cookie
@login_required
def other_profile_action(request, username):
    other_user = get_object_or_404(User, username=username)
    other_profile = get_object_or_404(Profile, user=other_user)

    current_profile = request.user.profile
    is_following = FollowRelationship.objects.filter(follower=current_profile, following=other_profile).exists()

    context = {
        'other_user': other_user,
        'other_profile': other_profile,
        'is_following': is_following
    }
    return render(request, 'socialnetwork/otherProfile.html', context)


@login_required
@ensure_csrf_cookie
def global_stream_action(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.posted_by = request.user
            new_post.post_date_time = timezone.now()
            new_post.save()
            return redirect('globalStream')
    
    return render(request, 'socialnetwork/globalStream.html', {'form': PostForm()})



def get_global(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    if request.method != 'GET':
        return JsonResponse({"error": "Invalid method"}, status=405)

    posts = Post.objects.all().order_by('-post_date_time')
    response_data=[]

    for post in posts:
        post_data={
            'id':post.id,
            'text': post.post_input_text,
            'author': {'id':post.posted_by.id, 'first_name':post.posted_by.first_name, 'last_name':post.posted_by.last_name, 'username': post.posted_by.username},
            'timestamp': post.post_date_time.isoformat(),
            'comments': []
        }
        comments = post.comment_set.all().order_by('timestamp')
        for comment in comments:
            comment_data = {
                "id": comment.id,
                "text": comment.text,
                "author": {"id": comment.user.id,"first_name": comment.user.first_name,"last_name": comment.user.last_name, "username": comment.user.username},
                "timestamp": comment.timestamp.isoformat()
            }
            post_data["comments"].append(comment_data)
        response_data.append(post_data)
    return JsonResponse(response_data, safe=False)



def add_post(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid method"}, status=405)
    
    form = PostForm(request.POST)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.posted_by = request.user
        new_post.save()
        post_data = {
            'id': new_post.id,
            'text': new_post.post_input_text,
            'author': {
                'id': new_post.posted_by.id,
                'first_name': new_post.posted_by.first_name,
                'last_name': new_post.posted_by.last_name,
                'username': new_post.posted_by.username
            },
            'timestamp': new_post.post_date_time.isoformat(),
            'comments': []
        }
        return JsonResponse(post_data, status=201)
    return JsonResponse({'errors': form.errors}, status=400)



@ensure_csrf_cookie
@login_required
def follower_stream_action(request):
    current_profile = request.user.profile
    following_profiles = current_profile.following.all()
    following_users = User.objects.filter(profile__in=following_profiles)
    posts = Post.objects.filter(posted_by__in=following_users).order_by('-post_date_time')
    context = {'posts': posts}
    return render(request, 'socialnetwork/followerStream.html', context)



def get_follower(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    if request.method != 'GET':
        return JsonResponse({"error": "Invalid method"}, status=405)

    current_profile = request.user.profile
    following_profiles = current_profile.following.all()
    
    following_users = [profile.user for profile in following_profiles]
    posts = Post.objects.filter(posted_by__in=following_users).order_by('-post_date_time')
    
    response_data = []
    for post in posts:
        post_data={
            'id':post.id,
            'text': post.post_input_text,
            'author': {'id':post.posted_by.id, 'first_name':post.posted_by.first_name, 'last_name':post.posted_by.last_name, 'username': post.posted_by.username},
            'timestamp': post.post_date_time.isoformat(),
            'comments': []
        }
        comments = post.comment_set.all().order_by('timestamp')
        for comment in comments:
            comment_data = {
                "id": comment.id,
                "text": comment.text,
                "author": {"id": comment.user.id,"first_name": comment.user.first_name,"last_name": comment.user.last_name,"username": comment.user.username},
                "timestamp": comment.timestamp.isoformat()
            }
            post_data["comments"].append(comment_data)
        response_data.append(post_data)
    return JsonResponse(response_data, safe=False)


def add_comment(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid method"}, status=405)
    
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    comment_text = request.POST.get('comment_text')
    post_id = request.POST.get('post_id')

    if not comment_text or not post_id:
        return JsonResponse({"error": "Missing parameters"}, status=400)
    if len(comment_text.strip()) == 0:
        return JsonResponse({"error": "Comment cannot be empty"}, status=400)
    if len(comment_text) > 200:
        return JsonResponse({"error": "Comment too long (max 200 characters)"}, status=400)
    
    try:
        post_id_int = int(post_id)
        try:
            post = Post.objects.get(id=post_id_int)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found"}, status=400)
    except ValueError:
        return JsonResponse({"error": "Invalid post ID"}, status=400)
    
    new_comment = Comment.objects.create(
        post=post,
        user=request.user,
        text=comment_text,
        timestamp=timezone.now()
    )

    comment_data = {
        "id": new_comment.id,
        "text": new_comment.text,
        "author": {"id": new_comment.user.id,"first_name": new_comment.user.first_name,"last_name": new_comment.user.last_name,"username": new_comment.user.username},
        "timestamp": new_comment.timestamp.isoformat(),
        "post_id": post.id
    }

    return JsonResponse(comment_data, status=200)



def index_action(request):
    if request.user.is_authenticated:
        return redirect('globalStream')
    else:
        return redirect('login')
    

@login_required
def follow_action(request, username):
    target_user = get_object_or_404(User, username=username)
    target_profile = get_object_or_404(Profile, user=target_user)

    current_profile = request.user.profile
    
    FollowRelationship.objects.get_or_create(
        follower=current_profile,
        following=target_profile
    )
    return redirect('other_profile', username=username)

@login_required
def unfollow_action(request, username):
    target_user = get_object_or_404(User, username=username)
    target_profile = get_object_or_404(Profile, user=target_user)
    
    current_profile = request.user.profile
    
    FollowRelationship.objects.filter(
        follower=current_profile,
        following=target_profile
    ).delete()
    return redirect('other_profile', username=username)



def get_photo(request, id):
    profile = get_object_or_404(Profile, id=id)
    print(f'Picture #{id} fetched from db: {profile.picture} (content_type={profile.content_type}, type of file={type(profile.picture)})')

    if not profile.picture:
        raise Http404
    
    return HttpResponse(profile.picture, content_type=profile.content_type)