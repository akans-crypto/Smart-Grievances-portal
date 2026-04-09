from django.urls import path
from grienvances.views import (
    dashboard, register, login_view, logout_view,
    submit_complaint, complaint_list, complaint_detail,
    leave_feedback, admin_dashboard, update_status,
    search_complaints,homepage, profile, contact_view
)

urlpatterns = [
    # User Dashboard
    path("",homepage, name= "homepage"),
    path("dashboard/", dashboard, name="dashboard"),

    # Authentication
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),


    # Complaints
    path("complaint_list/", complaint_list, name="complaint_list"),
    path("complaints/<int:pk>/", complaint_detail, name="complaint_detail"),
    path("submitcomplaint/", submit_complaint, name="submit_complaint"),

    # Feedback
    path("feedback/<int:pk>/", leave_feedback, name="leave_feedback"),

    # Admin
    path("admin_dashboard/", admin_dashboard, name="admin_dashboard"),

    # API / AJAX
    path('complaints/<int:pk>/update-status/', update_status, name='update_status'),

    # Search
    path("search/", search_complaints, name="search_complaints"),

    path("profile/", profile, name="profile"),

    path("contact/", contact_view, name="contact")
]
