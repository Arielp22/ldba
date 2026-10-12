# armenia/serializers/user.py
from rest_framework import serializers
from django.contrib.auth.models import User


class RegisterSerializer(serializers.Serializer):
    username  = serializers.CharField(max_length=150)
    email     = serializers.EmailField()
    password  = serializers.CharField(min_length=8, write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('This username is already taken.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email is already registered.')
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    """
    Vista completa del usuario para staff.
    El campo num_orders se incorpora en la Etapa 5
    una vez que el modelo Order esté disponible.
    """
    class Meta:
        model  = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_staff', 'is_active', 'date_joined',
        ]
        read_only_fields = ['id', 'date_joined']


class UserProfileSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()
    is_superuser = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email",
            "first_name", "last_name",
            "is_staff", "is_superuser", "groups",
        ]
        read_only_fields = ["id", "is_staff", "is_superuser", "groups"]

    def get_groups(self, obj):
        return list(obj.groups.values_list("name", flat=True))

    def validate_email(self, value):
        request = self.context.get("request")
        if User.objects.filter(email=value).exclude(pk=request.user.pk).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password     = serializers.CharField(min_length=8, write_only=True)
    new_password2    = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': 'Passwords do not match.'})
        return data