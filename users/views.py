from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .utils.otp_utils import send_otp_email, verify_otp
from bookbus.utils import transaction_utils

from django.contrib.auth import get_user_model


User = get_user_model()

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Store form data in session
            request.session['registration_data'] = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password1'],
                'first_name': form.cleaned_data.get('first_name', ''),
                'last_name': form.cleaned_data.get('last_name', ''),
            }
            
            # Send OTP (without user reference)
            try:
                send_otp_email(
                    email=form.cleaned_data['email'],
                    purpose='registration'
                )
                messages.info(request, 'OTP sent to your email. Please verify to complete registration.')
                return redirect('verify_email')
                
            except Exception as e:
                messages.error(request, f'Failed to send OTP: {str(e)}')
                return redirect('register')
                
    else:
        form = UserRegisterForm()
    
    return render(request, 'users/register.html', {'form': form})

def verify_email(request):
    # Check for registration data
    registration_data = request.session.get('registration_data')
    if not registration_data:
        messages.warning(request, 'No registration in progress.')
        return redirect('register')
    
    if request.method == "POST":
        otp_code = request.POST.get('otp')
        
        # Verify OTP
        success, message, otp_obj = verify_otp(
            email=registration_data['email'],
            otp_code=otp_code,
            purpose='registration'
        )
        
        if success:
            # Create user only after successful verification
            user = User.objects.create_user(
                username=registration_data['username'],
                email=registration_data['email'],
                password=registration_data['password'],
                first_name=registration_data['first_name'],
                last_name=registration_data['last_name'],
                is_active=True  # Immediately active
            )
            
            # Update OTP record with user reference
            otp_obj.user = user
            otp_obj.save()
            
            # Clean up session
            del request.session['registration_data']
            
            messages.success(request, 'Registration complete! You can now login.')
            return redirect('login')
            
        messages.error(request, f'Verification failed: {message}')
    
    return render(request, 'users/verify_email.html', {
        'email': registration_data['email']
    })

def resend_otp(request):
    registration_data = request.session.get('registration_data')
    if not registration_data:
        messages.warning(request, 'No registration in progress.')
        return redirect('register')
    
    try:
        send_otp_email(
            email=registration_data['email'],
            purpose='registration'
        )
        messages.info(request, 'New OTP sent successfully.')
    except Exception as e:
        messages.error(request, f'Failed to resend OTP: {str(e)}')
    
    return redirect('verify_email')


@login_required
def profile(request):
    if request.method == "POST":
        if 'update_profile' in request.POST:
            u_form = UserUpdateForm(request.POST, instance=request.user)
            if u_form.is_valid():
                u_form.save()
                messages.success(request, 'Account has been updated!')
                return redirect("profile")
        
        elif 'add_coins' in request.POST:
            amount = int(request.POST.get('coin_amount', 0))
            try:
                create_transaction(
                    user=request.user,
                    travels=None,
                    amount=amount,
                    transaction_type='ADD_MONEY',
                )
                messages.success(request, f'Successfully added {amount} coins!')
            except Exception as e:
                messages.error(request, f'Error adding coins: {str(e)}')
            return redirect("profile")
    
    else:
        u_form = UserUpdateForm(instance=request.user)
        
    context = {
        'u_form': u_form,
    }
    
    return render(request, 'users/profile.html', context)