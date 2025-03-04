from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Article
from apps.users.models import Category

# Create your views here.


def homepage(request):
    # Get latest 10 articles
    articles = Article.objects.all().order_by('-published_at')[:10]
    return render(request, 'news/homepage.html', {'articles': articles})


def search_articles(request):
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    source_slug = request.GET.get('source', '')

    # 1. Build the base queryset
    articles = Article.objects.all()

    # 2. Apply search filters
    if query:
        articles = articles.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    if category_slug:
        articles = articles.filter(category__slug=category_slug)

    if source_slug:
        articles = articles.filter(source__slug=source_slug)

    # 3. Wrap queryset in a Paginator (e.g., 9 results per page)
    paginator = Paginator(articles, 9)

    # 4. Get current page number from the request
    page_number = request.GET.get('page')

    # 5. Retrieve the specific page
    page_obj = paginator.get_page(page_number)

    # 6. Prepare context
    context = {
        'page_obj': page_obj,
        'articles': page_obj.object_list,       # The articles on this page
        'is_paginated': page_obj.has_other_pages(),
        'query': query,
        'category_slug': category_slug,
        'source_slug': source_slug,
    }

    return render(request, "news/search_results.html", context)


def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    return render(request, "news/article_detail.html", {"article": article})
