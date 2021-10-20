from django.urls import path
from . import views

app_name = 'booktest_v1'

urlpatterns = [
    path('books/', views.BookListView.as_view()),
    path('books/<int:pk>/', views.BookDetailView.as_view())
]
