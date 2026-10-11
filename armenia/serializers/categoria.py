from rest_framework import serializers
from armenia.models import Categoria


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "descripcion", "activa", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]