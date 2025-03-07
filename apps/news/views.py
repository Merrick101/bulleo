from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from .models import Article
from apps.users.forms import CommentForm
from apps.users.models import Category, Comment


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

    # Sorting Logic
    sort_order = request.GET.get("sort", "newest")
    if sort_order == "newest":
        comments = article.comments.all().order_by("-created_at")
    elif sort_order == "oldest":
        comments = article.comments.all().order_by("created_at")
    elif sort_order == "most_upvoted":
        comments = article.comments.all().annotate(
            upvote_count=Count("upvotes"),
            downvote_count=Count("downvotes")
        ).order_by("-upvote_count")
    else:
        comments = article.comments.all()

    context = {
        "article": article,
        "comments": comments,
        "sort_order": sort_order,
        "form": CommentForm(),
    }
    return render(request, "news/article_detail.html", context)


@login_required
def vote_comment(request, comment_id, action):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.method == "POST":
        if action == "upvote":
            comment.upvotes.add(request.user)
            comment.downvotes.remove(request.user)  # Remove any existing downvote
        elif action == "downvote":
            comment.downvotes.add(request.user)
            comment.upvotes.remove(request.user)  # Remove any existing upvote

        return JsonResponse({
            "success": True,
            "upvotes": comment.upvote_count(),
            "downvotes": comment.downvote_count(),
        })

    return JsonResponse({"success": False})


@login_required
def post_comment(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.article = article
            comment.created_at = now()
            comment.save()

            return JsonResponse({
                "success": True,
                "username": comment.user.username,
                "content": comment.content,
                "created_at": comment.created_at.strftime("%b %d, %Y %I:%M %p"),
                "comment_id": comment.id,
            })

    return JsonResponse({"success": False, "error": "Invalid data."}, status=400)


@login_required
def edit_comment(request, comment_id):
    """Allows users to edit their own comments."""
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)

    if request.method == "POST":
        new_content = request.POST.get("content", "").strip()
        if not new_content:
            return JsonResponse({"success": False, "error": "Comment cannot be empty."}, status=400)

        comment.content = new_content
        comment.created_at = now()  # Update timestamp
        comment.save()

        return JsonResponse({
            "success": True,
            "comment_id": comment.id,
            "updated_content": comment.content,
            "updated_at": comment.created_at.strftime("%b %d, %Y %I:%M %p"),
        })

    return JsonResponse({"success": False, "error": "Invalid request."}, status=400)


@login_required
def delete_comment(request, comment_id):
    """Allows users to delete their own comments."""
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)

    if request.method == "POST":
        comment.delete()
        return JsonResponse({"success": True, "comment_id": comment_id})

    return JsonResponse({"success": False, "error": "Invalid request."}, status=400)
