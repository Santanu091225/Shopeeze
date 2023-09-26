from django.urls import path
from accounts.views import login_page, signup_page, activate_email


urlpatterns = [
    path('login/', login_page, name='login'),
    path('sign-up/', signup_page, name='signup'),
    path('activate/<email_token>/', activate_email, name='activate_email'),
]

