from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json
from .models import Profile

ERR_INVALID_REQUEST = {'error': 'Invalid request'}

User = get_user_model()

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
        
        user = authenticate(request, username=user.username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Login successful'})
        return JsonResponse({'error': 'Invalid credentials'}, status=401)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already registered'}, status=400)
        User.objects.create(
            username=email,
            email=email,
            password=make_password(password),
            first_name=name
        )
        return JsonResponse({'message': 'Registration successful'})
    return JsonResponse(ERR_INVALID_REQUEST, status=400)

@csrf_exempt
def password_recovery_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        if not User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email not found'}, status=404)
        # Simulate sending a recovery email
        send_mail(
            'Password Recovery',
            'Click the link to reset your password.',
            'noreply@example.com',
            [email],
            fail_silently=False,
        )
        return JsonResponse({'message': 'Password recovery email sent'})
    return JsonResponse(ERR_INVALID_REQUEST, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return JsonResponse({'message': 'Logged out'})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def profile_view(request):
    # Require authenticated session
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    # Ensure profile exists
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        data = {
            'email': request.user.email,
            'name': f"{request.user.first_name} {request.user.last_name}".strip(),
            'region': profile.region,
            'comuna': profile.comuna,
            'telefono': profile.telefono,
            'rut': profile.rut,
            'direccion': profile.direccion,
            'sede': profile.sede,
            'facultades': profile.facultades,
            'carreras': profile.carreras,
        }
        return JsonResponse(data)

    # POST: update profile
    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    request.user.first_name = payload.get('name', request.user.first_name) or request.user.first_name
    request.user.save(update_fields=['first_name'])

    for field in ['region', 'comuna', 'telefono', 'rut', 'direccion', 'sede']:
        if field in payload:
            setattr(profile, field, payload[field] or '')

    if 'facultades' in payload:
        profile.facultades = payload.get('facultades') or []
    if 'carreras' in payload:
        profile.carreras = payload.get('carreras') or []

    profile.save()
    return JsonResponse({'message': 'Profile updated'})