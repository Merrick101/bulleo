from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from .models import Article
from apps.users.forms import CommentForm
from apps.users.models import Comment


def homepage(request):
    """
    Render the homepage with the latest 10 articles.
    """
    articles = Article.objects.all().order_by('-published_at')[:10]
    return render(request, 'news/homepage.html', {'articles': articles})


def search_articles(request):
    """
    Search for articles by query, category, and source.
    Paginate results with 9 articles per page.
    """
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    source_slug = request.GET.get('source', '')

    articles = Article.objects.all()

    if query:
        articles = articles.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    if category_slug:
        articles = articles.filter(category__slug=category_slug)

    if source_slug:
        articles = articles.filter(source__slug=source_slug)

    paginator = Paginator(articles, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'articles': page_obj.object_list,
        'is_paginated': page_obj.has_other_pages(),
        'query': query,
        'category_slug': category_slug,
        'source_slug': source_slug,
    }

    return render(request, "news/search_results.html", context)


def get_sorted_comments(article, sort_order):
    """
    Retrieve and sort top-level comments for the given article based on sort_order.
    """
    comments = article.comments.filter(parent__isnull=True)
    sort_options = {
        "newest": "-created_at",
        "oldest": "created_at",
        "most_upvoted": "-upvote_count"
    }
    sort_field = sort_options.get(sort_order, "-created_at")
    if sort_order == "most_upvoted":
        comments = comments.annotate(upvote_count=Count("upvotes"))
    return comments.order_by(sort_field)


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
    Top-level comments are filtered (parent is null) and replies are pre-fetched.
    Sorting is applied based on the GET parameter 'sort'.
    """
    article = get_object_or_404(Article, id=article_id)
    sort_order = request.GET.get("sort", "newest")
    comments = article.comments.filter(parent__isnull=True)

    if sort_order == "newest":
        comments = comments.order_by("-created_at")
    elif sort_order == "oldest":
        comments = comments.order_by("created_at")
    elif sort_order == "most_upvoted":
        comments = comments.annotate(upvote_count=Count("upvotes")).order_by("-upvote_count")

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
    """
    comment = get_object_or_404(Comment, id=comment_id)

    if request.method == "POST":
        if action == "upvote":
            comment.upvotes.add(request.user)
            comment.downvotes.remove(request.user)
        elif action == "downvote":
            comment.downvotes.add(request.user)
            comment.upvotes.remove(request.user)

        return JsonResponse({
            "success": True,
            "upvotes": comment.upvote_count(),
            "downvotes": comment.downvote_count(),
        })
    return JsonResponse({"success": False}, status=400)


@login_required
def post_comment(request, article_id):
    """
    Handle posting a new comment or reply using CommentForm for validation.
    """
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article_id = article_id
            comment.user = request.user
            parent_comment_id = form.cleaned_data.get("parent_comment_id")
            if parent_comment_id:
                comment.parent = get_object_or_404(Comment, id=parent_comment_id)
            comment.save()

            return JsonResponse({
                'success': True,
                'comment_id': comment.id,
                'username': comment.user.username,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'parent_comment_id': parent_comment_id
            })
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
    return JsonResponse({"success": False, "error": "Invalid request."}, status=400)


@login_required
def edit_comment(request, comment_id):
    """
    Allow users to edit their own comments.
    """
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
    """
    Allow users to delete their own comments.
    """
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    if request.method == "POST":
        comment.delete()
        return JsonResponse({"success": True, "comment_id": comment_id})
    return JsonResponse({"success": False, "error": "Invalid request."}, status=400)


@login_required
def reply_to_comment(request, article_id, parent_comment_id):
    """
    Handle replies to comments by linking a new comment to the parent.
    """
    parent_comment = get_object_or_404(Comment, id=parent_comment_id)
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if not content:
            return JsonResponse({"success": False, "error": "Reply content cannot be empty."}, status=400)
        new_comment = Comment.objects.create(
            user=request.user,
            article_id=article_id,
            content=content,
            parent=parent_comment
        )
        response_data = {
            'success': True,
            'message': 'Reply submitted successfully!',
            'comment_id': new_comment.id,
            'content': new_comment.content,
            'created_at': new_comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'parent_comment_id': parent_comment_id,
            'username': new_comment.user.username,
        }
        return JsonResponse(response_data)
    return JsonResponse({'success': False, 'message': 'Failed to submit reply.'}, status=400)


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
    return JsonResponse({"success": False, "error": "Invalid request."}, status=400)
