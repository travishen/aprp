from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string

from . import models
from . import forms

import json
import requests


def post_socialwall(request):

    url = 'http://localhost:8000/posts/api/'
    res = requests.get(url)
    data = json.loads(res.content)
    post_list = data

    form = forms.PostForm()

    return render(request, 'socialwall.html', locals())


def post_new_form(request):

    form = forms.PostForm()
    html = render_to_string('form.html', {'form': form}, request=request)

    return JsonResponse(html, safe=False)


def post_edit_form(request):
    pass
