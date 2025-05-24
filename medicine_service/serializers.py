from rest_framework import serializers
from bson import ObjectId
from .models import Medicine


class MedicineSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    
    class Meta:
        model = Medicine
        exclude = ['_id']
    
    def get_id(self, obj):
        if hasattr(obj, '_id'):
            return str(obj._id)
        return None
        
        
class MedicineDetailSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    
    class Meta:
        model = Medicine
        exclude = ['_id']
        
    def get_id(self, obj):
        if hasattr(obj, '_id'):
            return str(obj._id)
        return None 