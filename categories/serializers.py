from rest_framework import serializers
from categories.models import Category

class CategorySerializer(serializers.ModelSerializer):
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ["id", "name", "description", "created_at", "task_count"]
        read_only_fields = ["id", "created_at", "task_count"]
    
    def get_task_count(self, obj):
        return obj.tasks.count()
