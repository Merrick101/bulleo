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
        'articles': page_obj.object_list,  # The articles on this page
        'is_paginated': page_obj.has_other_pages(),
        'query': query,
        'category_slug': category_slug,
        'source_slug': source_slug,
    }

    return render(request, "news/search_results.html", context)


def get_sorted_comments(article, sort_order):
    """
    Retrieve and sort comments based on the provided sort order.
    """
    comments = article.comments.filter(parent__isnull=True)

    # Define sorting options
    sort_options = {
        "newest": "-created_at",
        "oldest": "created_at",
        "most_upvoted": "-upvote_count"
    }

    # Default to 'newest' if the sort_order is invalid
    sort_field = sort_options.get(sort_order, "-created_at")

    # Apply sorting
    if sort_order == "most_upvoted":
        comments = comments.annotate(upvote_count=Count("upvotes"))

    return comments.order_by(sort_field)


def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    sort_order = request.GET.get("sort", "newest")
    comments = article.comments.filter(parent__isnull=True)
    if sort_order == "newest":
        comments = comments.order_by("-created_at")
    elif sort_order == "oldest":
        comments = comments.order_by("created_at")
    elif sort_order == "most_upvoted":
        comments = comments.annotate(upvote_count=Count("upvotes")).order_by("-upvote_count")

    # Pass the count of top-level comments and replies to the template
    comment_count = comments.count() + sum([comment.replies.count() for comment in comments])

    context = {
        "article": article,
        "comments": comments.prefetch_related("replies"),
        "sort_order": sort_order,
        "form": CommentForm(),
        "comment_count": comment_count,  # Pass total count to the template
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
    if request.method == "POST":
        content = request.POST.get('content')
        parent_comment_id = request.POST.get('parent_comment_id')

        if not content.strip():  # Validate that content is not empty
            return JsonResponse({"success": False, "error": "Comment cannot be empty."}, status=400)

        parent_comment = None
        if parent_comment_id:
            parent_comment = get_object_or_404(Comment, id=parent_comment_id)

        comment = Comment.objects.create(
            user=request.user,
            article_id=article_id,
            content=content,
            parent=parent_comment  # Ensure this is linked to the parent comment for replies
        )

        return JsonResponse({
            'success': True,
            'comment_id': comment.id,
            'username': comment.user.username,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'parent_comment_id': parent_comment_id
        })

    return JsonResponse({"success": False, "error": "Invalid request."}, status=400)


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


@login_required
def reply_to_comment(request, article_id, parent_comment_id):
    # Retrieve the parent comment
    parent_comment = get_object_or_404(Comment, id=parent_comment_id)

    if request.method == "POST":
        # Get content of the reply from the request
        content = request.POST.get("content", "").strip()

        if not content:
            return JsonResponse({"success": False, "error": "Reply content cannot be empty."}, status=400)

        # Create the new reply comment
        new_comment = Comment.objects.create(
            user=request.user,
            article_id=article_id,
            content=content,
            parent=parent_comment  # This links the reply to the parent comment
        )

        # Return the success response with relevant comment data
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

    return JsonResponse({'success': False, 'message': 'Failed to submit reply.'})
