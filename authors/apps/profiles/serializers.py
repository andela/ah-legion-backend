from rest_framework import serializers

from .models import Profile


class GetProfileSerializer(serializers.ModelSerializer):
    """
    serializers for user profile upon user registration.
    """

    username = serializers.ReadOnlyField(source='get_username')
    image_url = serializers.ReadOnlyField(source='get_cloudinary_url')

    class Meta:
        model = Profile

        fields = (
            'username', 'first_name', 'last_name', 'bio', 'image', 'image_url',
            'website', 'city', 'phone', 'country')

        read_only_fields = ("created_at", "updated_at")
