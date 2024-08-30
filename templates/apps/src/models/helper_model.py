from django.db import models

class Configuration(models.Model):
    logo = models.CharField(max_length=100, blank=True, null=True)
    loader = models.TextField(blank=True, null=True)
    page_limit = models.IntegerField(blank=True, null=True)
    is_active = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'configuration'
            

    
