from django.urls import path
from . import views, admin



urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('logout/', views.logoutUser, name='logout'),
    path('sell/', views.sell_order, name='sell'),
    path('buy/', views.buy_order, name='buy'),
    path('your/orders/', views.your_orders, name='your_orders'),
    path('all/pending/orders/', views.all_pending_orders, name='all_pending_orders'),#JsonResponse su tutti gli ordini pendenti - Loggarsi con un admin per accedere
    path('all/closed/orders/', views.all_closed_orders, name='all_closed_orders'),
    path('my/data/', views.my_data, name='my_data'),
    path('buy/verification', views.buy_transaction_verification, name='buy_transaction_verification'),
    path('sell/verification', views.sell_transaction_verification, name='sell_transaction_verification'),
]
