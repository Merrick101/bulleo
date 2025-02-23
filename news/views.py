from django.http import HttpResponse

# Create your views here.


def my_news(request):
    return HttpResponse("Hello, World!")
