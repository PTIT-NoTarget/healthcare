from djongo import models
from django import forms
import json
from bson import ObjectId


class ListField(models.Field):
    """Custom field to store lists in MongoDB compatible with djongo 1.3.6"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return json.loads(value)
    
    def to_python(self, value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return json.loads(value)
    
    def get_prep_value(self, value):
        if value is None:
            return []
        return json.dumps(value)


class Medicine(models.Model):
    # Explicitly define _id field for MongoDB
    _id = models.ObjectIdField(primary_key=True, default=ObjectId)
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200)
    manufacturer = models.CharField(max_length=200)
    description = models.TextField()
    dosage_form = models.CharField(max_length=50)  # tablet, capsule, liquid, etc.
    strength = models.CharField(max_length=50)  # e.g., 500mg, 10mg/ml
    ndc_code = models.CharField(max_length=50, unique=True)  # National Drug Code
    price = models.DecimalField(max_digits=10, decimal_places=2)
    requires_prescription = models.BooleanField(default=True)
    is_controlled_substance = models.BooleanField(default=False)
    control_class = models.CharField(max_length=5, blank=True, null=True)  # I, II, III, IV, V
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # MongoDB specific fields using custom ListField for compatibility
    side_effects = ListField(default=list)
    interactions = ListField(default=list)
    contraindications = ListField(default=list)
    active_ingredients = ListField(default=list)
    
    class Meta:
        db_table = 'medicines'

    def __str__(self):
        return f"{self.name} ({self.strength})"

