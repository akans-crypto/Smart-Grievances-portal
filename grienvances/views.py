from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Count, Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from grienvances.forms import SimpleUserCreationForm

from grienvances.models import Complaint, Response, Feedback
from grienvances.forms import ComplaintForm, ResponseForm, FeedbackForm, ContactForm
from grienvances.nlp_utils import simple_sentiment, priority_from_sentiment

import json

def homepage(request):
    return render(request,"homepage.html")

# -----------------------------
# Helper Functions
# -----------------------------
def is_admin(user):
    return user.is_staff


# -----------------------------
# Authentication Views
# -----------------------------
def register(request):
    if request.method == "POST":
        form = SimpleUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")  # redirect to dashboard after signup
    else:
        form = SimpleUserCreationForm()
    return render(request, "registration.html", {"form": form})


def login_view(request):
    """User login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, '⚠️ Invalid username or password.')
    return render(request, 'login.html')


@login_required
def logout_view(request):
    """Logout user"""
    logout(request)
    return redirect('login')


# -----------------------------
# User Dashboard
# -----------------------------
@login_required
def dashboard(request):
    pending_count = Complaint.objects.filter(status="Pending").count()
    inprogress_count = Complaint.objects.filter(status="In_Progress").count()
    resolved_count = Complaint.objects.filter(status="Resolved").count()

    # For Chart.js
    status_data = {
        "labels": ["Pending", "In Progress", "Resolved"],
        "data": [pending_count, inprogress_count, resolved_count],
    }

    category_qs = Complaint.objects.values("category").annotate(total=Count("id"))
    category_data = {
        "labels": [c["category"] for c in category_qs],
        "data": [c["total"] for c in category_qs],
    }

    context = {
        "pending_count": pending_count,
        "inprogress_count": inprogress_count,
        "resolved_count": resolved_count,
        "status_data": json.dumps(status_data),
        "category_data": json.dumps(category_data),
        "recent_complaints": Complaint.objects.order_by("-created_at")[:5],
    }
    if request.user.is_superuser or request.user.is_staff:
        return render(request, "admin_dashboard.html", context)
    else:
        return render(request, "student_dashboard.html", context)


# -----------------------------
# Complaints (User & Admin)
# -----------------------------
@login_required
def submit_complaint(request):
    """Submit new complaint"""
    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            messages.success(request, "✅ Complaint submitted successfully!")
            return redirect("complaint_list")
        messages.error(request, "⚠️ Please correct the errors in the form.")
    else:
        form = ComplaintForm()
    return render(request, "submit_complaint.html", {"form": form})


@login_required
def complaint_list(request):
    """List complaints (admin sees all, users see their own)"""
    if request.user.is_staff:
        qs = Complaint.objects.all().order_by('-created_at')
    else:
        qs = Complaint.objects.filter(user=request.user).order_by('-created_at')

    # Filters
    q = request.GET.get('q', '').strip()
    category = request.GET.get('category')
    status = request.GET.get('status')

    if q:
        qs = qs.filter(Q(subject__icontains=q) | Q(description__icontains=q))
    if category:
        qs = qs.filter(category=category)
    if status:
        qs = qs.filter(status=status)

    paginator = Paginator(qs, 10)
    page = request.GET.get('page')
    complaints = paginator.get_page(page)

    return render(request, 'complaint_list.html', {'complaints': complaints})


@login_required
def complaint_detail(request, pk):
    """Complaint details + admin response"""
    complaint = get_object_or_404(Complaint, pk=pk)

    if not request.user.is_staff and complaint.user != request.user:
        return HttpResponseForbidden("❌ You are not allowed to view this complaint.")

    # Navigation
    if request.user.is_staff:
        prev_c = Complaint.objects.filter(id__lt=complaint.id).order_by('-id').first()
        next_c = Complaint.objects.filter(id__gt=complaint.id).order_by('id').first()
    else:
        prev_c = Complaint.objects.filter(user=request.user, id__lt=complaint.id).order_by('-id').first()
        next_c = Complaint.objects.filter(user=request.user, id__gt=complaint.id).order_by('id').first()

    response_form = None
    if request.user.is_staff:
        if request.method == 'POST':
            response_form = ResponseForm(request.POST)
            if response_form.is_valid():
                r = response_form.save(commit=False)
                r.complaint = complaint
                r.admin = request.user
                r.save()
                # Update complaint status
                new_status = request.POST.get('status')
                if new_status in dict(Complaint._meta.get_field('status').choices):
                    complaint.status = new_status
                    complaint.save()
                messages.success(request, '✅ Response added successfully.')
                return redirect('complaint_detail', pk=pk)
        else:
            response_form = ResponseForm()

    return render(request, 'complaint_detail.html', {
        'complaint': complaint,
        'response_form': response_form,
        'previous_complaint': prev_c,
        'next_complaint': next_c
    })


# -----------------------------
# Feedback
# -----------------------------
@login_required
def leave_feedback(request, pk):
    """Leave feedback after complaint resolution"""
    complaint = get_object_or_404(Complaint, pk=pk, user=request.user)
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            fb = form.save(commit=False)
            fb.complaint = complaint
            fb.save()
            messages.success(request, '🙏 Thanks for your feedback!')
            return redirect('complaint_detail', pk=pk)
    else:
        form = FeedbackForm()
    return render(request, 'feedback.html', {'form': form, 'complaint': complaint})


# -----------------------------
# Admin Dashboard
# -----------------------------
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard with statistics and complaints overview"""
    total_complaints = Complaint.objects.count()
    pending_complaints = Complaint.objects.filter(status="Pending").count()
    inprogress_complaints = Complaint.objects.filter(status="In_Progress").count()
    resolved_complaints = Complaint.objects.filter(status="Resolved").count()

    recent_complaints = Complaint.objects.order_by('-created_at')[:5]
    users = User.objects.all()

    categories = Complaint.objects.values("category").distinct()
    category_data = [
        {"name": cat["category"], "count": Complaint.objects.filter(category=cat["category"]).count()}
        for cat in categories
    ]

    context = {
        "total_complaints": total_complaints,
        "pending_complaints": pending_complaints,
        "inprogress_complaints": inprogress_complaints,
        "resolved_complaints": resolved_complaints,
        "recent_complaints": recent_complaints,
        "users": users,
        "categories": category_data,
    }
    return render(request, "admin_dashboard.html", context)


# -----------------------------
# API Endpoints
# -----------------------------
@login_required

def update_status(request, pk):
    if request.method == "POST":
        new_status = request.POST.get("status")
        try:
            complaint = Complaint.objects.get(pk=pk)
            complaint.status = new_status
            complaint.save()
            return JsonResponse({"success": True, "status": new_status})
        except Complaint.DoesNotExist:
            return JsonResponse({"success": False, "error": "Complaint not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})


@login_required
def search_complaints(request):
    """Search complaints by subject/description"""
    q = request.GET.get('q', '')
    qs = Complaint.objects.filter(Q(subject__icontains=q) | Q(description__icontains=q))
    return render(request, 'complaint_list.html', {'complaints': qs})

def profile(request):
    # Get complaints of the logged-in student
    complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "profile.html", {"complaints": complaints})


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # Save message in DB
            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')  # refresh page after submit
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})