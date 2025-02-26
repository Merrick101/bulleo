from django.shortcuts import render

# Create your views here.


def discussion_page(request):
    return render(request, 'community/discussion.html')
