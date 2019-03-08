from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='get_username')
    email = serializers.ReadOnlyField(source='get_email')

    class Meta:
        model = Profile
        fields = [
            'username', 'first_name', 'last_name', 'email', 'birth_date', 'bio',
            'image', 'city', 'country', 'phone', 'website', 'created_at',
            'updated_at'
        ]
