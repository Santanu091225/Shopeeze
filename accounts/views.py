from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from .models import *
from products.models import *
from base.send__otp import MessageHandler
import razorpay
import random
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os


def login_page(request):
    if not request.user.is_authenticated:
        return render(request, "accounts/login.html")

    else:
        return HttpResponseRedirect(request.path_info)


def login_with_otp(request):
    if request.method == "POST":
        try:
            phone_number = request.POST.get("phone_number")

            if not User.objects.filter(username=phone_number).exists():
                messages.warning(request, "Account does not exist. Sign up first.")
                return redirect("signup")

            profile = Profile.objects.filter(phone_number=phone_number).first()

            otp = random.randint(1000, 9999)

            profile.otp = otp
            profile.save()

            message_handler = MessageHandler(phone_number, otp).send_otp_on_phone()

            return redirect(f"/accounts/OTP-verify/{profile.uid}")

        except Exception as e:
            print(e)


def login_with_password(request):
    if request.method == "POST":
        try:
            phone_number = request.POST.get("phone_number")
            password = request.POST.get("password")

            user = User.objects.filter(username=phone_number)

            if not user.exists():
                messages.warning(request, "Account does not exist. Sign up first.")
                return HttpResponseRedirect(request.path_info)

            if not user.first().profile.is_new_user:
                otp = random.randint(1000, 9999)

                profile = Profile.objects.filter(phone_number=phone_number)[0]
                profile.otp = otp
                profile.save()

                message_handler = MessageHandler(phone_number, otp).send_otp_on_phone()

                messages.warning(
                    request,
                    "Seems like you are not verify your mobile no. Try to verify it first.",
                )
                return redirect(f"/accounts/OTP-verify/{profile.uid}")

            user = authenticate(username=phone_number, password=password)

            if user:
                login(request, user)

                profile = Profile.objects.get(user=user)
                profile.is_phone_no_verified = True
                profile.save()

                return redirect("/")

        except Exception as e:
            print(e)
            messages.error(request, "Something went wrong")
            return HttpResponse(f"{e}")


def signup_page(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            try:
                first_name = request.POST.get("first_name")
                last_name = request.POST.get("last_name")
                phone_number = request.POST.get("phone_number")
                email = request.POST.get("email", "")
                password = request.POST.get("password")

                if not User.objects.filter(username=phone_number).exists():

                    user = User.objects.create(
                        username=phone_number,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                    )

                    user.set_password(password)
                    user.save()

                    otp = random.randint(1000, 9999)

                    profile = Profile.objects.create(
                        user=user,
                        is_phone_no_verified=False,
                        phone_number=phone_number,
                        otp=otp,
                    )

                    message_handler = MessageHandler(
                        phone_number=phone_number, otp=otp
                    ).send_otp_on_phone()

                    return redirect(f"/accounts/OTP-verify/{profile.uid}/")

                else:
                    messages.warning(request, "Phone number already exists")
                    return HttpResponseRedirect(request.path_info)

            except Exception as e:
                print(e)

        return render(request, "accounts/signup.html")

    else:
        return redirect("index")


def otp_verify_page(request, uid):
    profile = get_object_or_404(Profile, uid=uid)

    if request.method == "POST":
        try:
            first_number = request.POST.get("first_number")
            second_number = request.POST.get("second_number")
            third_number = request.POST.get("third_number")
            fourth_number = request.POST.get("fourth_number")

            otp = int(first_number + second_number + third_number + fourth_number)

            if otp == profile.otp:
                profile.is_new_user = True
                profile.is_phone_no_verified = True
                profile.save()

                user = User.objects.get(username=profile.phone_number)

                login(request, user)

                return redirect("/")

            else:
                messages.error(request, "Incorrect OTP")
                return redirect(f"/accounts/OTP-verify/{uid}/")

        except Exception as e:
            print(e)
            messages.error(request, "something went wrong")
    return render(
        request,
        "accounts/verify-otp.html",
        {"profile": profile, "masked_phone_number": str(profile.phone_number)[-3:]},
    )


def resend_otp(request, uid):
    profile = get_object_or_404(Profile, uid=uid)
    phone_number = profile.phone_number

    otp = random.randint(1000, 9999)
    message_handler = MessageHandler(
        phone_number=phone_number, otp=otp
    ).send_otp_on_phone()
    messages.success(request, "Successfully resend OTP.")
    return redirect(f"/accounts/OTP-verify/{uid}/")


def userLogout(request):
    profile = Profile.objects.get(user=request.user)
    profile.is_phone_no_verified = False
    profile.save()

    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect("login")


def edit_profile(request):
    if request.user.is_authenticated:
        user = request.user
        profile = user.profile

        if request.method == "POST":
            user.first_name = request.POST.get("first_name", user.first_name)
            user.last_name = request.POST.get("last_name", user.last_name)
            user.email = request.POST.get("email", user.email)
            user.save()


            if request.FILES.get("profile_image"):
                old_image_path = (
                    profile.profile_image.path
                )  # Get the path of the old image
                if os.path.exists(old_image_path):  # Check if the old image file exists
                    os.remove(old_image_path)  # Delete the old image file
                uploaded_file = request.FILES["profile_image"]
                file_extension = os.path.splitext(uploaded_file.name)[1]
                new_filename = f"{user.first_name}_{user.last_name}_pp_{profile.uid}{file_extension}"
                profile.profile_image.save(new_filename, uploaded_file)
            profile.save()

            messages.success(request, "Profile updated successfully")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        return render(request, "accounts/edit_profile.html", {"profile": profile})

    messages.warning(request, "You have to login first")
    return redirect("login")


def saved_addresses(request):
    if request.user.is_authenticated:
        addresses = Address.objects.filter(profile=request.user.profile)
        return render(request, "accounts/manage_address.html", {"addresses": addresses})

    else:
        messages.warning(request, "You have to login first")
        return redirect("login")



def edit_address_profile(request, uid):
    if request.user.is_authenticated:
        address = Address.objects.get(uid=uid)
        if request.method == 'POST':
            address.receiver = request.POST.get("updated_receiver")
            address.mobile = request.POST.get("updated_mobile")
            address.home = request.POST.get("updated_home")
            address.city = request.POST.get("updated_city")
            address.pincode = request.POST.get("updated_pincode")
            address.district = request.POST.get("updated_district")
            address.state = request.POST.get("updated_state")
            address.landmark = request.POST.get("updated_landmark")
            address.save()

            messages.success(request, "Adress has been updated")
            return redirect('saved_addresses')


        return render(request, 'accounts/edit_address.html', {'address': address, 'state_choices': Address.STATE_CHOICES})


    else:
        messages.error(request, "you must be logged in first")
        return redirect('login')



def add_address_profile(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                receiver = request.POST.get('receiver')
                mobile = request.POST.get('mobile')
                home = request.POST.get('home')
                city = request.POST.get('city')
                pincode = request.POST.get('pincode')
                district = request.POST.get('district')
                state = request.POST.get('state')
                landmark = request.POST.get('landmark', '')
                

                Address.objects.create(profile=request.user.profile, receiver=receiver, mobile=mobile, home=home, city=city, pincode=pincode, district=district, state=state, landmark=landmark)

                messages.success(request, 'Address added successfully')
                return redirect('saved_addresses')

            except Exception as e:
                print(e)
                messages.error(request, "An error occurred")


        return render(request, 'accounts/add_address.html', {'state_choices': Address.STATE_CHOICES})

    else:
        messages.error(request, 'You have to log in first')
        return redirect('login')




def add_to_cart(request, uid):
    if request.user.is_authenticated:
        if request.method == "GET":
            color = request.GET.get("color")
            size = request.GET.get("size")

            color = get_object_or_404(Color, color_name=color)
            size = get_object_or_404(SizeVariant, size_name=size)

            product = Product.objects.get(uid=uid)
            user = request.user
            cart, _ = Cart.objects.get_or_create(user=user)

            cart_item = CartItems.objects.filter(
                cart=cart, product=product, color=color, size=size
            ).first()

            if cart_item and cart_item.quantity < 5:
                cart_item.quantity += 1
                cart_item.save()

            elif cart_item and cart_item.quantity == 5:
                messages.warning(
                    request, "You have already reached the maximum quantity"
                )
                return redirect(request.META.get("HTTP_REFERER", "/"))

            else:
                cart_item = CartItems.objects.create(
                    cart=cart, product=product, size=size, color=color, quantity=1
                )
                cart_item.save()

            redirect_url = f"{request.META.get('HTTP_REFERER', '/')}&size={size}"

            messages.success(request, "Item added successfully to your bag")
            return redirect(redirect_url)
    else:
        messages.error(request, "You must be logged in to add items to the cart.")
        return redirect("login")


shipping_charge = 50


def cart_view(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItems.objects.filter(cart=cart)
        sections = Category.objects.values_list("section", flat=True).distinct()
        categories = Category.objects.all()

        for cart_item in cart_items:
            first_image = ProductImage.objects.filter(
                product=cart_item.product, color=cart_item.color
            ).first()
            cart_item.first_image = first_image

        total_price = sum(
            item.quantity * item.product.discount_price for item in cart_items
        )

        context = {
            "cart_items": cart_items,
            "total_price": total_price,
            "categories": categories,
            "sections": sections,
        }

        if total_price < 1000:
            subtotal = total_price
            context["subtotal"] = subtotal
            total_price += shipping_charge
            context["new_total_price"] = total_price

        return render(request, "cart/cart.html", context)

    else:
        messages.error(request, "You must be logged in to add items to the cart")
        return redirect("login")


def increase_quantity(request, uid):
    if request.user.is_authenticated:
        cart_item = CartItems.objects.filter(uid=uid).first()

        if cart_item.quantity < 5:
            cart_item.quantity += 1
            cart_item.save()

        else:
            messages.warning(request, "maximum quantity reached")

        return redirect("cart")

    else:
        messages.error(request, "You must be logged in")
        return redirect("login")


def decrease_quantity(request, uid):
    if request.user.is_authenticated:
        cart_item = CartItems.objects.filter(uid=uid).first()

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()

        else:
            messages.warning(request, "minimum quantity reached")

        return redirect("cart")

    else:
        messages.error(request, "You must be logged in to add items to the cart")
        return redirect("login")


def remove_item(request, uid):
    if request.user.is_authenticated:
        cart_item = CartItems.objects.filter(uid=uid).first()

        if cart_item:
            cart_item.delete()

        else:
            messages.error(request, "an error occurred")

        return redirect("cart")

    else:
        messages.error(request, "You must be logged in to add items to the cart")
        return redirect("login")


def address_list(request):
    if request.user.is_authenticated:
        addresses = Address.objects.filter(profile__user=request.user)
        state_choices = Address.STATE_CHOICES

        context = {"addresses": addresses, "state_choices": state_choices}
        return render(request, "address/address.html", context)

    return redirect("login")


def add_address(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            receiver = request.POST.get("receiver")
            mobile = request.POST.get("mobile")
            home = request.POST.get("home")
            city = request.POST.get("city")
            pincode = request.POST.get("pincode")
            district = request.POST.get("district")
            state = request.POST.get("state")
            landmark = request.POST.get("landmark")

            address = Address.objects.create(
                profile=request.user.profile,
                receiver=receiver,
                mobile=mobile,
                home=home,
                city=city,
                pincode=pincode,
                district=district,
                state=state,
                landmark=landmark,
            )

            messages.success(request, "Your address has been successfully saved")

            return redirect(request.META.get("HTTP_REFERER", "/"))

    messages.warning(request, "You have to login first.")
    return redirect("login")


def edit_address_cart(request, uid):
    if request.user.is_authenticated:
        address = get_object_or_404(Address, uid=uid)
        state_choices = Address.STATE_CHOICES

        if request.method == "POST":

            address.receiver = request.POST.get("updated_receiver")
            address.mobile = request.POST.get("updated_mobile")
            address.home = request.POST.get("updated_home")
            address.city = request.POST.get("updated_city")
            address.pincode = request.POST.get("updated_pincode")
            address.district = request.POST.get("updated_district")
            address.state = request.POST.get("updated_state")
            address.landmark = request.POST.get("updated_landmark")
            address.save()

            messages.success(request, "Adress has been updated")
            return redirect('address')

        return render(
            request,
            "address/editAddress.html",
            {"address": address, "state_choices": state_choices},
        )

    else:
        messages.warning(request, "You have to login first.")
        return redirect("login")


def remove_address(request, uid):
    if request.user.is_authenticated:
        address = Address.objects.get(uid=uid)

        if address:
            address.delete()

        else:
            messages.error(request, "an error occured")

        return redirect(request.META.get("HTTP_REFERER", "/"))

    else:
        messages.warning(request, "You have to login first.")
        return redirect("login")


from django.conf import settings

client = razorpay.Client(auth=(settings.RZP_KEY_ID, settings.RZP_SECRET_KEY))


def make_payment_view(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            cart_items = CartItems.objects.filter(cart__user=request.user)

            address_uid = request.POST.get("address_uid")
            delivery_address = Address.objects.get(uid=address_uid)

            amount = sum(
                item.quantity * item.product.discount_price for item in cart_items
            )

            if amount < 1000:
                amount += shipping_charge

            order, _ = Order.objects.get_or_create(
                user=request.user, amount=amount, delivery_address=delivery_address
            )

            for cart_item in cart_items:
                order_item, _ = OrderItem.objects.get_or_create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    size=cart_item.size,
                    color=cart_item.color,
                )

            payment = client.order.create(
                {
                    "amount": amount * 100,
                    "currency": "INR",
                    "receipt": str(order.order_id),
                    "payment_capture": 0,
                }
            )

            order.rzp_order_id = payment["id"]
            order.save()
            print("\n")
            print(payment)
            print("\n")

            context = {"payment": payment}
            return render(request, "payment/makePayment.html", context)

    else:
        messages.warning(request, "You have to login first.")
        return redirect("login")


from django.views.decorators.csrf import csrf_exempt
from razorpay.errors import SignatureVerificationError


@csrf_exempt
def payment_capture(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get("razorpay_payment_id", "")
            order_id = request.POST.get("razorpay_order_id", "")
            payment_signature = request.POST.get("razorpay_signature", "")

            params = {
                "razorpay_payment_id": payment_id,
                "razorpay_order_id": order_id,
                "razorpay_signature": payment_signature,
            }

            print(params)
            print("\n")

            try:
                order = get_object_or_404(Order, rzp_order_id=order_id)
                response = client.utility.verify_payment_signature(params)
            except SignatureVerificationError as e:
                print(e)
                return HttpResponse("Payment verification failed")

            if response:

                amount = order.amount * 100

                order.rzp_payment_id = payment_id
                order.rzp_payment_signature = payment_signature
                order.save()

                try:
                    client.payment.capture(payment_id, amount)
                    order.payment_status = "Successful"
                    order.save()

                    return HttpResponse("Payment successful")

                except Exception as e:
                    print(e)
                    order.payment_status = "Failed"
                    order.save()
                    return HttpResponse("Payment failed")

        except Exception as e:
            print(e)
            return HttpResponse(e)
