from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
import json
from datetime import timedelta
from .models import ClinicSetting, Patient, Token
from .utils import haversine
from django.db.models import Max

def index(request):
    """ Patient Portal - Show Generate Token form or current Token status """
    token_id = request.session.get('current_token_id')
    if token_id:
        try:
            token = Token.objects.get(id=token_id, date=timezone.now().date())
            if token.status not in ['COMPLETED', 'CANCELLED', 'SKIPPED']:
                return render(request, 'queue_board/patient_dashboard.html', {'token': token})
        except Token.DoesNotExist:
            request.session.pop('current_token_id', None)

    clinic = ClinicSetting.objects.first()
    return render(request, 'queue_board/index.html', {'clinic': clinic})

@csrf_exempt
def generate_token(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        dept = request.POST.get('department', 'GENERAL')

        # Basic validation
        if not name or not phone or len(phone) != 10 or not phone.isdigit():
            messages.error(request, 'Please enter a valid name and 10-digit phone number.')
            return redirect('index')

        # Get or create patient record
        patient, _ = Patient.objects.get_or_create(
            phone_number=phone, defaults={'name': name}
        )

        # Check if patient already has an active token for today
        existing_token = Token.objects.filter(
            patient=patient,
            date=timezone.now().date(),
            status__in=['INACTIVE', 'ACTIVE', 'SERVING']
        ).first()

        if existing_token:
            messages.info(request, f'You already have Token #{existing_token.token_number} for today. Showing your status.')
            request.session['current_token_id'] = existing_token.id
            return redirect('index')

        # Check clinic daily token limit
        clinic = ClinicSetting.objects.first()
        today_count = Token.objects.filter(date=timezone.now().date()).count()
        max_tokens = clinic.max_tokens_per_day if clinic else 50

        if today_count >= max_tokens:
            messages.error(request, f'Sorry, the clinic has reached its maximum capacity of {max_tokens} patients for today. Please visit tomorrow.')
            return redirect('index')

        # Generate new token number
        last_token = Token.objects.filter(date=timezone.now().date()).aggregate(Max('token_number'))['token_number__max']
        next_number = (last_token or 0) + 1

        token = Token.objects.create(
            patient=patient,
            token_number=next_number,
            department=dept,
            status='INACTIVE'
        )

        request.session['current_token_id'] = token.id
        messages.success(request, f'Token #{token.token_number} generated successfully! Please proceed to the clinic.')
        return redirect('index')
    return redirect('index')

@csrf_exempt
def activate_token(request):
    """ Called via JS Geolocation """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lat = data.get('lat')
            lng = data.get('lng')
            token_id = request.session.get('current_token_id')
            
            if not token_id or not lat or not lng:
                return JsonResponse({'error': 'Invalid request'}, status=400)
                
            token = Token.objects.get(id=token_id, date=timezone.now().date())
            clinic = ClinicSetting.objects.first()
            if not clinic:
                return JsonResponse({'error': 'Clinic configuration missing'}, status=500)
                
            distance = haversine(clinic.latitude, clinic.longitude, float(lat), float(lng))
            
            if distance <= 1000:
                if token.status == 'INACTIVE':
                    token.status = 'ACTIVE'
                    token.activated_at = timezone.now()
                    token.save()
                return JsonResponse({'success': True, 'status': token.status, 'distance': round(distance)})
            else:
                return JsonResponse({'success': False, 'message': f'You are {round(distance)}m away. Move closer (1km) to activate.', 'distance': round(distance)})
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def queue_status_api(request):
    """ API for polling by patients/staff """
    # Auto-expire tokens older than 120 minutes that are still inactive
    expiration_time = timezone.now() - timedelta(minutes=120)
    Token.objects.filter(
        date=timezone.now().date(),
        status='INACTIVE',
        generated_at__lt=expiration_time
    ).update(status='CANCELLED')

    current_serving = Token.objects.filter(date=timezone.now().date(), status='SERVING').order_by('token_number').first()
    
    token_id = request.session.get('current_token_id')
    user_status = None
    estimated_wait = 0
    token_number = None

    if token_id:
        try:
            token = Token.objects.get(id=token_id)
            user_status = token.status
            token_number = token.token_number
            estimated_wait = token.get_estimated_wait_minutes()
        except Token.DoesNotExist:
            pass
            
    # Patients waiting
    waiting_count = Token.objects.filter(date=timezone.now().date(), status='ACTIVE').count()
    last_issued = Token.objects.filter(date=timezone.now().date()).aggregate(Max('token_number'))['token_number__max']

    return JsonResponse({
        'serving': current_serving.token_number if current_serving else '-',
        'last_issued': last_issued or '-',
        'user_token': token_number,
        'user_status': user_status,
        'estimated_wait': estimated_wait,
        'waiting_count': waiting_count
    })

def staff_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('staff_dashboard')
        
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('staff_dashboard')
        else:
            return render(request, 'queue_board/staff_login.html', {'error': 'Invalid credentials or non-staff user.'})
    return render(request, 'queue_board/staff_login.html')

def staff_logout_view(request):
    logout(request)
    return redirect('staff_login')

@login_required(login_url='staff_login')
def staff_dashboard(request):
    serving_tokens = Token.objects.filter(date=timezone.now().date(), status='SERVING').order_by('token_number')
    active_tokens = Token.objects.filter(date=timezone.now().date(), status='ACTIVE').order_by('token_number')
    inactive_tokens = Token.objects.filter(date=timezone.now().date(), status='INACTIVE').order_by('token_number')
    total_today = Token.objects.filter(date=timezone.now().date()).count()
    return render(request, 'queue_board/staff_dashboard.html', {
        'serving_tokens': serving_tokens,
        'active_tokens': active_tokens,
        'inactive_tokens': inactive_tokens,
        'total_today': total_today,
    })

@csrf_exempt
@login_required(login_url='staff_login')
def staff_action(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        token_id = request.POST.get('token_id')
        
        try:
            if action == 'CALL_NEXT':
                # Complete existing serving if any
                Token.objects.filter(date=timezone.now().date(), status='SERVING').update(status='COMPLETED')
                
                # Get next active
                next_token = Token.objects.filter(date=timezone.now().date(), status='ACTIVE').first()
                if next_token:
                    next_token.status = 'SERVING'
                    next_token.save()
            elif token_id:
                token = Token.objects.get(id=token_id)
                if action == 'COMPLETE':
                    token.status = 'COMPLETED'
                    token.save()
                elif action == 'SKIP':
                    token.status = 'SKIPPED'
                    token.save()
                elif action == 'ACTIVATE':
                    token.status = 'ACTIVE'
                    token.activated_at = timezone.now()
                    token.save()
            return redirect('staff_dashboard')
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return redirect('staff_dashboard')

@csrf_exempt
@login_required(login_url='staff_login')
def staff_manual_booking(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        is_prio = request.POST.get('is_priority') == 'on'
        
        patient, _ = Patient.objects.get_or_create(phone_number=phone, defaults={'name': name})
        
        # Check if patient already has an active/serving token
        existing_token = Token.objects.filter(
            patient=patient, 
            date=timezone.now().date(),
            status__in=['INACTIVE', 'ACTIVE', 'SERVING']
        ).first()

        if existing_token:
            return redirect('staff_dashboard')

        # Generate new token
        last_token = Token.objects.filter(date=timezone.now().date()).aggregate(Max('token_number'))['token_number__max']
        next_number = (last_token or 0) + 1
        
        Token.objects.create(
            patient=patient,
            token_number=next_number,
            status='ACTIVE', # Automatic active for staff booking
            is_priority=is_prio,
            activated_at=timezone.now()
        )
    return redirect('staff_dashboard')

