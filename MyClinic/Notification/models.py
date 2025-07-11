from django.db import models
import os
class Notification(models.Model):
    TAG_CHOICES = [
        ('health_tip', 'Health Tip'),
        ('general', 'General'),
        # ('reminder', 'Reminder'),
        ('promotion', 'Promotion'),
        ('alert', 'Alert'),
    ]
    title = models.CharField(max_length=255)
    body = models.TextField()
    image = models.FileField(upload_to='notifications/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    tags = models.CharField(max_length=50, choices=TAG_CHOICES, default='general')
    created_at = models.DateTimeField(auto_now_add=True)
    # target_role = models.CharField(max_length=20, choices=[('patient', 'Patient'), ('doctor', 'Doctor'), ('all', 'All')], default='all')

    def __str__(self):
        return self.title
    
    def delete(self, *args, **kwargs):
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)  # This deletes the image file
        super().delete(*args, **kwargs)
