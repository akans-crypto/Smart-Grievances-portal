# forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Complaint, Feedback, Response, ContactMessage


# ---------------------------
# User Registration Form
# ---------------------------
class SimpleUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ["username", "password1", "password2"]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

# ---------------------------
# User Login Form
# ---------------------------
class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


# ---------------------------
# Complaint Form
# ---------------------------

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['subject','description', 'category', 'attachment']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter subject'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

# ---------------------------
# Feedback Form
# ---------------------------
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["rating", "comments"]  # ✅ use "comments", not "comment"
        widgets = {
            "rating": forms.Select(choices=[(5,"★★★★★"),(4,"★★★★"),(3,"★★★"),(2,"★★"),(1,"★")], attrs={"class":"form-select"}),
            "comments": forms.Textarea(attrs={"class":"form-control", "rows":3, "placeholder":"Your feedback..."}),
        }

class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Enter response"}),
        }

class ContactForm(forms.Form):
    name = forms.CharField(
        label="Your Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-transparent text-dark border border-primary shadow-sm',
            'placeholder': 'Enter your name'
        })
    )
    email = forms.EmailField(
        label="Your Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control bg-transparent text-dark border border-primary shadow-sm',
            'placeholder': 'Enter your email'
        })
    )
    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={
            'class': 'form-control bg-transparent text-dark border border-primary shadow-sm',
            'rows': 4,
            'placeholder': 'Type your message...'
        })
    )