from django.db import models

class Configuration(models.Model):
    logo = models.CharField(max_length=100, blank=True, null=True)
    loader = models.TextField(blank=True, null=True)
    page_limit = models.IntegerField(blank=True, null=True)
    org_name = models.CharField(max_length=500, blank=True, null=True)
    org_code = models.CharField(max_length=6, blank=True, null=True)
    google_app_key = models.CharField(max_length=500, blank=True, null=True)
    firebase_server_key = models.TextField(blank=True, null=True)
    order_timing = models.CharField(max_length=50, blank=True, null=True)
    user_tracking_time = models.CharField(max_length=50, blank=True, null=True)
    travel_amount = models.IntegerField(blank=True, null=True)
    office_start_time = models.CharField(max_length=10, blank=True, null=True)
    office_end_time = models.CharField(max_length=10, blank=True, null=True)
    travel_charge  = models.FloatField(default=1)
    org_latitude = models.CharField(max_length=50, blank=True, null=True)
    org_longitude = models.CharField(max_length=50, blank=True, null=True)
    
    is_active = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'configuration'
            

    
