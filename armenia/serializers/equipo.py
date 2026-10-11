from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers

from armenia.models.equipo import Equipo, EquipoTemporadaCategoria
from armenia.models.temporada import Temporada
from armenia.models.categoria import Categoria


class EquipoSerializer(serializers.ModelSerializer):
    """Lectura de equipo, incluye datos del usuario asociado."""
    username = serializers.CharField(source="user.username", read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = Equipo
        fields = [
            "id", "nombre", "siglas", "color_principal", "color_secundario",
            "logo", "presidente", "telefono", "email", "activo",
            "user_id", "username",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "user_id", "username", "created_at", "updated_at"]


class EquipoCreateSerializer(serializers.Serializer):
    """
    Crea Equipo + User en una sola transacción.
    El username y password se generan o se reciben desde el Superadmin.
    """
    # Datos del equipo
    nombre = serializers.CharField(max_length=150)
    siglas = serializers.CharField(max_length=10, required=False, allow_blank=True)
    color_principal = serializers.CharField(max_length=30, required=False, allow_blank=True)
    color_secundario = serializers.CharField(max_length=30, required=False, allow_blank=True)
    logo = serializers.CharField(max_length=255, required=False, allow_blank=True)
    presidente = serializers.CharField(max_length=150, required=False, allow_blank=True)
    telefono = serializers.CharField(max_length=30, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    activo = serializers.BooleanField(required=False, default=True)

    # Datos del usuario asociado
    username = serializers.CharField(max_length=150, write_only=True)
    password = serializers.CharField(min_length=8, write_only=True)

    def validate_nombre(self, value):
        if Equipo.objects.filter(nombre__iexact=value).exists():
            raise serializers.ValidationError("Ya existe un equipo con este nombre.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este username ya está en uso.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        username = validated_data.pop("username")
        password = validated_data.pop("password")

        user = User.objects.create_user(
            username=username,
            password=password,
            email=validated_data.get("email") or "",
        )
        # Asignar grupo "Administrador Equipo"
        from django.contrib.auth.models import Group
        grupo, _ = Group.objects.get_or_create(name="Administrador Equipo")
        user.groups.add(grupo)

        equipo = Equipo.objects.create(user=user, **validated_data)
        return equipo


class EquipoUpdateSerializer(serializers.ModelSerializer):
    """Actualización parcial del equipo (no toca el User)."""

    class Meta:
        model = Equipo
        fields = [
            "nombre", "siglas", "color_principal", "color_secundario",
            "logo", "presidente", "telefono", "email", "activo",
        ]

    def validate_nombre(self, value):
        qs = Equipo.objects.filter(nombre__iexact=value).exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe un equipo con este nombre.")
        return value


class EquipoTemporadaCategoriaSerializer(serializers.ModelSerializer):
    equipo_nombre = serializers.CharField(source="equipo.nombre", read_only=True)
    temporada_nombre = serializers.CharField(source="temporada.nombre", read_only=True)
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)

    class Meta:
        model = EquipoTemporadaCategoria
        fields = [
            "id",
            "equipo", "equipo_nombre",
            "temporada", "temporada_nombre",
            "categoria", "categoria_nombre",
            "activo", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ResetPasswordEquipoSerializer(serializers.Serializer):
    """Cambio de contraseña por Superadmin (cambio de presidente)."""
    new_password = serializers.CharField(min_length=8, write_only=True)
    new_password2 = serializers.CharField(min_length=8, write_only=True)

    def validate(self, data):
        if data["new_password"] != data["new_password2"]:
            raise serializers.ValidationError(
                {"new_password2": "Las contraseñas no coinciden."}
            )
        return data