from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Article
from users.models import Category

# Create your views here.


def homepage(request):
    # Get latest 10 articles
    articles = Article.objects.all().order_by('-published_at')[:10]
    return render(request, 'news/homepage.html', {'articles': articles})


def search_articles(request):
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    source_slug = request.GET.get('source', '')

    articles = Article.objects.all()

    if query:
        articles = articles.filter(Q(title__icontains=query) | Q(content__icontains=query))

    if category_slug:
        articles = articles.filter(category__slug=category_slug)

    if source_slug:
        articles = articles.filter(source__slug=source_slug)

    context = {
        'articles': articles,
        'query': query,
    }
    return render(request, "news/search_results.html", context)


def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    return render(request, "news/article_detail.html", {"article": article})
