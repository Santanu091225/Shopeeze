from django.urls import path
from .views import *


urlpatterns = [
    path("login/", login_page, name="login"),
    path("login-with-otp/", login_with_otp, name="login_OTP"),
    path("login-with-password/", login_with_password, name="login_Pass"),
    path("logout/", userLogout, name="logout"),
    path("sign-up/", signup_page, name="signup"),
    path("OTP-verify/<uid>/", otp_verify_page, name="otp_verify"),
    path("resend-OTP/<uid>/", resend_otp, name="resend_otp"),


    path("profile/edit-profile/", edit_profile, name="edit_profile"),
    path("profile/saved-addresses/", saved_addresses, name="saved_addresses"),
    path("profile/saved-addresses/remove-address/<uid>/", remove_address, name="remove_address"),
    path("profile/saved-addresses/add-address/", add_address_profile, name="add_address_profile"),
    path("profile/saved-addresses/edit-address/<uid>/", edit_address_profile, name="edit_address"),


    path("add-to-cart/<uid>/", add_to_cart, name="add_to_cart"),
    path("cart/", cart_view, name="cart"),
    path("cart/add-qnty/<uid>/", increase_quantity, name="add_qnty"),
    path("cart/sub-qnty/<uid>/", decrease_quantity, name="sub_qnty"),
    path("cart/remove-item/<uid>/", remove_item, name="remove_item"),
    path("cart/address/", address_list, name="address"),
    path("cart/add-address/", add_address, name="add_address"),
    path("cart/edit-address/<uid>/", edit_address_cart, name="edit_address_page_cart"),
    path("cart/make-payment/", make_payment_view, name="make_payment"),
    path("cart/make-payment/payment-capture/", payment_capture, name="payment_capture"),
]
