from django.db import models
from django.contrib.auth.models import User



CATEGORY_CHOICES = [
        ('Academic', 'Academic'),
        ('Hostel', 'Hostel'),
        ('Mess', 'Mess'),
        ('Transport', 'Transport'),
        ('Library', 'Library'),
        ('Examination', 'Examination'),
        ('WiFi/Internet', 'WiFi/Internet'),
        ('Classroom Infrastructure', 'Classroom Infrastructure'),
        ('Sanitation', 'Sanitation'),
        ('Faculty', 'Faculty'),
        ('Fees/Billing', 'Fees/Billing'),
        ('Security', 'Security'),
        ('Ragging/Harassment', 'Ragging/Harassment'),
        ('Lab Equipment', 'Lab Equipment'),
        ('Canteen', 'Canteen'),
        ('Event Management', 'Event Management'),
        ('Sports/Gym', 'Sports/Gym'),
        ('Medical/Health', 'Medical/Health'),
        ('Scholarship', 'Scholarship'),
        ('Placement/Training', 'Placement/Training'),
        ('Others', 'Others'),
    ]


STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
]


PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Normal', 'Normal'),
        ('High', 'High'),
        ]

class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200) 
    description = models.TextField()
    attachment = models.FileField(upload_to='attachments/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=[("Pending","Pending"),("In Progress","In Progress"),("Resolved","Resolved")], default="Pending")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="Medium") 
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True, null=True)  # <-- Add this
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



# smart fields (fill later via simple rules)
    sentiment_score = models.FloatField(blank=True, null=True)


def __str__(self):
        return f"Complaint by {self.user} ({self.status})"



class Response(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="responses")
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


def __str__(self):
    return f"Response to {self.complaint.subject}"



class Feedback(models.Model):
    complaint = models.OneToOneField(Complaint, on_delete=models.CASCADE, related_name="feedback")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comments = models.TextField(blank=True, null=True)  # <-- Notice plural "comments"
    created_at = models.DateTimeField(auto_now_add=True)


def __str__(self):
    return f"Feedback on {self.complaint.subject}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"