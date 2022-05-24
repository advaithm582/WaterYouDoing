from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from evaluator.forms import EvaluatorForm
from landing.models import UserProfile


@login_required
def evaluate(request):
    if request.method == 'POST':
        # get form data from post
        form = EvaluatorForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # if profile with given username already exists, update profile. 
            # otherwise make profile for user
            try:
                profile = UserProfile.objects.get(user=request.user)
                profile.weekly_laundry_loads = data['weekly_laundry_loads']
                profile.washer_type = data['washer_type']
                profile.daily_bathroom_trips = data['daily_bathroom_trips']
                profile.weekly_showers = data['weekly_showers']
                profile.shower_head = data['shower_head']
                profile.shower_times = data['shower_times']
                profile.weekly_baths = data['weekly_baths']
                profile.weekly_dishes = data['weekly_dishes']
                profile.weekly_sprinkler = data['weekly_sprinkler']
                profile.swimming_pool = data['swimming_pool']
            except UserProfile.DoesNotExist:
                profile = UserProfile(user=request.user, weekly_laundry_loads = data['weekly_laundry_loads'],
                                      washer_type=data['washer_type'], 
                                      daily_bathroom_trips = data['daily_bathroom_trips'],
                                      weekly_showers = data['weekly_showers'], 
                                      shower_times = data['shower_times'], 
                                      shower_head=data['shower_head'], 
                                      weekly_baths = data['weekly_baths'], 
                                      weekly_dishes = data['weekly_dishes'], 
                                      weekly_sprinkler = data['weekly_sprinkler'], 
                                      swimming_pool = data['swimming_pool'])
            # store profile in db
            profile.save()
            return HttpResponse(request, 'Success!')

    # send html on non-POST requests
    return render(request, 'evaluate_2.html', context={"form":EvaluatorForm()})


@login_required
def result(request, username=None):
    # find profile
    try:
        if username:
            user = User.objects.get(username=username)
            profile = UserProfile.objects.get(user=user)
        else:
            profile = UserProfile.objects.get(user=request.user)
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        return render(request, 'error.html', status=400)
    # assign tier and message
    if profile.score > settings.AVG_WEEKLY_WATER_HI * 1.20:
        tier = 'water-u-doing.matlab'
        css_class = 'red'
        message = 'BAD'
    elif profile.score > settings.AVG_WEEKLY_WATER_HI:
        tier = 'water-u-doing.php'
        css_class = 'orange'
        message = 'You really should start saving water.'
    elif settings.AVG_WEEKLY_WATER_LOW <= profile.score <= settings.AVG_WEEKLY_WATER_HI:
        tier = 'water-u-doing.java'
        css_class = 'yellow'
        message = 'Okay, but you could do better.'
    else:
        tier = 'water-u-doing.py'
        css_class = 'green'
        message = 'Good. Thanks for saving water!'
    context = {
        'user': request.user.username,
        'score': profile.score,
        'tier': tier,
        'class': css_class,
        'message': message
    }
    return render(request, 'results.html', context=context)


@login_required
def detail(request, username):
    try:
        user = User.objects.get(username=username)
        profile = UserProfile.objects.get(user=user)
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        return render(request, 'error.html', status=400)
    context = {'profile': profile}
    return render(request, 'details.html', context)


def learn_more(request):
    return HttpResponseRedirect('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
