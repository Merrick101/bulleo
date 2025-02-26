from django.urls import path
from .views import homepage  # Ensure homepage is correctly imported

urlpatterns = [
    path('', homepage, name='news_home'),  # News homepage
]
