from django.urls import path

from . import views

app_name = 'booktest_v4'
urlpatterns = [
    path('basic/', views.basic_view, name='basic_view'),
    path('session/', views.session_view, name='session_view'),
    path('token/', views.token_view, name='token_view'),
]
