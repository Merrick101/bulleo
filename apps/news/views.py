from django.shortcuts import render
from .models import Article

# Create your views here.


def homepage(request):
    # Get latest 10 articles
    articles = Article.objects.all().order_by('-published_at')[:10]
    return render(request, 'news/homepage.html', {'articles': articles})


def article_list(request):
    return render(request, "news/article_list.html")


def article_detail(request, article_id):
    article = Article.objects.get(id=article_id)
    return render(request, 'news/article_detail.html', {'article': article})
