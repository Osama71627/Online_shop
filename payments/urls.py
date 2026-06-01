from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('<int:order_id>/', views.payment_view, name='payment'),
    path('<int:order_id>/process/', views.process_payment, name='process'),
    path('<int:order_id>/success/', views.payment_success, name='success'),
    path('<int:order_id>/cancel/', views.payment_cancel, name='cancel'),
]
