"""
Views for the News application, handling article display,
search, comments, and user interactions.
Located at: apps/news/views.py
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, F, Max
from django.contrib.auth.decorators import login_required
from .models import Article, Category
from apps.users.forms import CommentForm
from apps.users.models import Comment


def chunked_queryset(queryset, chunk_size=3):
    """
    Splits a QuerySet or list into lists of size `chunk_size`.
    Returns a generator of sub-lists.
    """
    items = list(queryset)
    for i in range(0, len(items), chunk_size):
        yield items[i:i+chunk_size]


def homepage(request):
    # 1. Trending Articles (site-wide)
    trending_articles = (
        Article.objects
        .annotate(comment_count=Count('comments'))
        .order_by('-comment_count')[:8]
    )
    trending_chunks = list(chunked_queryset(trending_articles, 3))

    # 2. Latest Articles (site-wide)
    latest_articles = Article.objects.order_by('-published_at')[:12]
    latest_chunks = list(chunked_queryset(latest_articles, 3))

    # 3. Picked for You (per category) => two sub-sections:
    # "Trending in X" & "Latest in X"
    picked_articles_by_category = {}
    if request.user.is_authenticated:
        user_categories = request.user.profile.preferred_categories.all()
        for cat in user_categories:
            # a) Trending in this category
            cat_trending = (
                cat.articles.all()
                .annotate(comment_count=Count('comments'))
                .order_by('-comment_count')[:8]
            )
            cat_trending_chunks = list(chunked_queryset(cat_trending, 3))

            # b) Latest in this category
            cat_latest = (
                cat.articles.all()
                .order_by('-published_at')[:12]
            )
            cat_latest_chunks = list(chunked_queryset(cat_latest, 3))

            picked_articles_by_category[cat] = {
                'trending': {
                    'chunks': cat_trending_chunks,
                    'carousel_id': f'catTrendingCarousel-{cat.slug}',
                },
                'latest': {
                    'chunks': cat_latest_chunks,
                    'carousel_id': f'catLatestCarousel-{cat.slug}',
                },
            }

    context = {
        'trending_chunks': trending_chunks,
        'latest_chunks': latest_chunks,
        'picked_articles_by_category': picked_articles_by_category,
    }
    return render(request, 'news/homepage.html', context)


def about_view(request):
    return render(request, 'news/about.html')


def search_articles(request):
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    source_slug = request.GET.get('source', '')
    sort = request.GET.get('sort', 'relevant')

    articles = Article.objects.all()

    if query:
        articles = articles.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    if category_slug:
        articles = articles.filter(category__slug=category_slug)
        category_obj = Category.objects.filter(slug=category_slug).first()
        category_name = category_obj.name if category_obj else ''
    else:
        category_name = ''

    if source_slug:
        articles = articles.filter(source__slug=source_slug)

    # Sorting logic here ...
    if sort == 'recent':
        articles = articles.order_by('-published_at')
    elif sort == 'oldest':
        articles = articles.order_by('published_at')
    elif sort == 'category':
        articles = articles.order_by('category__name')
    elif sort == 'source':
        articles = articles.order_by('source__name')
    else:  # 'relevant' or unknown fallback
        articles = articles.order_by('-id')

    paginator = Paginator(articles, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'articles': page_obj.object_list,
        'is_paginated': page_obj.has_other_pages(),
        'query': query,
        'category_slug': category_slug,
        'category_name': category_name,
        'source_slug': source_slug,
        'sort': sort,
        'options': [
            "relevant", "recent", "oldest", "category", "source"
        ],
    }
    return render(request, "news/search_results.html", context)


@login_required
def toggle_like(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    user = request.user
    if user in article.likes.all():
        article.likes.remove(user)
        liked = False
    else:
        article.likes.add(user)
        liked = True
    return JsonResponse(
        {'success': True, 'liked': liked, 'likes_count': article.likes.count()}
    )


@login_required
def toggle_save(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    user = request.user
    if user in article.saves.all():
        article.saves.remove(user)
        saved = False
    else:
        article.saves.add(user)
        saved = True
    return JsonResponse(
        {'success': True, 'saved': saved, 'saves_count': article.saves.count()}
    )


def get_sorted_comments(article, sort_order):
    comments = article.comments.filter(parent__isnull=True)
    if sort_order == "most_upvoted":
        comments = comments.annotate(
            upvote_count=Count("upvotes")
        ).order_by("-upvote_count", "-created_at")
    elif sort_order == "newest":
        comments = comments.order_by("-created_at")
    elif sort_order == "oldest":
        comments = comments.order_by("created_at")
    return comments


def count_all_comments(comment_qs):
    """
    Recursively count all comments and nested replies in a QuerySet.
    """
    total = 0
    for comment in comment_qs:
        total += 1  # count this comment
        total += count_all_comments(comment.replies.all())
    return total


def article_detail(request, article_id):
    """
    Display article details along with its comments.
    Top-level comments are filtered (parent is null)
    and replies are pre-fetched.
    Sorting is applied based on the GET parameter 'sort'.
    """
    article = get_object_or_404(Article, id=article_id)

    # Create a unique key for this article in the session
    session_key = f'viewed_article_{article.id}'
    if not request.session.get(session_key, False):
        # Increment view count only if not viewed in this session
        article.views = F('views') + 1
        article.save(update_fields=['views'])
        article.refresh_from_db()
        # Mark this article as viewed in the session
        request.session[session_key] = True

    sort_order = request.GET.get("sort", "newest")

    unique_comment_ids = (
        article.comments.filter(parent__isnull=True)
        .values("user_id", "content")
        .annotate(latest_id=Max("id"))
        .values_list("latest_id", flat=True)
    )

    comments = (
        Comment.objects.filter(id__in=unique_comment_ids)
        .select_related("user")
        .prefetch_related("replies")
    )

    if sort_order == "newest":
        comments = comments.order_by("-created_at")
    elif sort_order == "oldest":
        comments = comments.order_by("created_at")
    elif sort_order == "most_upvoted":
        comments = comments.annotate(
            upvote_count=Count("upvotes")
        ).order_by("-upvote_count")

    # Recursively count all comments (top-level and nested replies)
    comment_count = count_all_comments(comments)

    context = {
        "article": article,
        "comments": comments.prefetch_related("replies"),
        "sort_order": sort_order,
        "form": CommentForm(),
        "comment_count": comment_count,
    }
    return render(request, "news/article_detail.html", context)


@login_required
def vote_comment(request, comment_id, action):
    """
    Handle AJAX request for upvoting or downvoting a comment.
    Block the action if the comment is deleted.
    """
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.deleted:
        return JsonResponse(
            {"success": False, "error":
                "Cannot vote on a deleted comment."}, status=400
        )

    if request.method == "POST":
        if action == "upvote":
            comment.upvotes.add(request.user)
            comment.downvotes.remove(request.user)
        elif action == "downvote":
            comment.downvotes.add(request.user)
            comment.upvotes.remove(request.user)

        return JsonResponse({
            "success": True,
            "upvotes": comment.upvotes.count(),
            "downvotes": comment.downvotes.count(),
        })
    return JsonResponse({"success": False}, status=400)


@login_required
def post_comment(request, article_id):
    if request.method == "POST":
        form = CommentForm(
            request.POST, user=request.user, article=get_object_or_404(
                Article, id=article_id
            )
        )
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article_id = article_id
            comment.user = request.user

            parent_comment_id = form.cleaned_data.get("parent_comment_id")
            if parent_comment_id:
                parent_comment = get_object_or_404(
                    Comment, id=parent_comment_id
                )
                if parent_comment.article_id != article_id:
                    return JsonResponse(
                        {"success": False, "error":
                            "Parent comment must belong to the same article."},
                        status=400
                    )
                if parent_comment.deleted:
                    return JsonResponse(
                        {"success": False, "error":
                            "Cannot reply to a deleted comment."},
                        status=400
                    )
                comment.parent = parent_comment

            comment.save()

            # Compute the updated comment count
            # (recursively count all top-level comments and their replies)
            top_level_comments = comment.article.comments.filter(
                parent__isnull=True
            )
            comment_count = count_all_comments(
                top_level_comments
            )

            return JsonResponse({
                'success': True,
                'comment_id': comment.id,
                'username': comment.user.username,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'parent_comment_id': parent_comment_id,
                'is_owner': True,
                'comment_count': comment_count
            })
        else:
            return JsonResponse({
                "success": False,
                "errors": form.errors,
                "message": form.errors.get(
                    "__all__", ["Invalid submission."]
                )[0]
            }, status=400)
    return JsonResponse(
        {"success": False, "error": "Invalid request."}, status=400
    )


@login_required
def edit_comment(request, comment_id):
    """
    Allow the owner of a comment to edit it, unless the comment is deleted.
    """
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    if comment.deleted:
        return JsonResponse(
            {"success": False, "error": "Cannot edit a deleted comment."},
            status=400
        )

    if request.method == "POST":
        new_content = request.POST.get("content", "").strip()
        if not new_content:
            return JsonResponse(
                {"success": False, "error": "Comment cannot be empty."},
                status=400
            )

        comment.content = new_content
        comment.save()

        return JsonResponse({
            "success": True,
            "comment_id": comment.id,
            "updated_content": comment.content,
            "updated_at": comment.updated_at.strftime("%b %d, %Y %I:%M %p"),
        })
    return JsonResponse(
        {"success": False, "error": "Invalid request."}, status=400
    )


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    if request.method == "POST":
        comment.delete()

        # Recompute total comment count for the article
        top_level_comments = comment.article.comments.filter(
            parent__isnull=True
        )
        comment_count = count_all_comments(
            top_level_comments
        )

        return JsonResponse({
            "success": True,
            "comment_id": comment.id,
            "deleted": True,
            "comment_count": comment_count
        })
    return JsonResponse(
        {"success": False, "error": "Invalid request."},
        status=400
    )


@login_required
def reply_to_comment(request, article_id, parent_comment_id):
    parent_comment = get_object_or_404(Comment, id=parent_comment_id)
    if parent_comment.deleted:
        return JsonResponse(
            {"success": False, "error":
                "Cannot reply to a deleted comment."},
            status=400
        )

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if not content:
            return JsonResponse(
                {"success": False, "error":
                    "Reply content cannot be empty."},
                status=400
            )

        new_comment = Comment.objects.create(
            user=request.user,
            article_id=article_id,
            content=content,
            parent=parent_comment
        )

        # Compute the updated comment count using the helper function
        top_level_comments = new_comment.article.comments.filter(
            parent__isnull=True
        )
        comment_count = count_all_comments(
            top_level_comments
        )

        return JsonResponse({
            'success': True,
            'comment_id': new_comment.id,
            'content': new_comment.content,
            'created_at': new_comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'parent_comment_id': parent_comment_id,
            'parent_level': request.POST.get("parent_level", 0),
            'username': new_comment.user.username,
            'is_owner': (request.user == new_comment.user),
            'comment_count': comment_count
        })
    return JsonResponse(
        {"success": False, "error": "Invalid request."}, status=400
    )


@login_required
def report_comment(request, comment_id):
    """
    Allow a user to report a comment as harmful.
    This view marks the comment as reported.
    """
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == "POST":
        comment.reported = True
        comment.save()
        return JsonResponse({"success": True, "comment_id": comment_id})
    return JsonResponse(
        {"success": False, "error":
            "Invalid request."},
        status=400
    )
