import factory

from django.contrib.auth import get_user_model


class UserFactory(factory.DjangoModelFactory):

    class Meta:
        model = get_user_model()

    username = factory.sequence(lambda x: f"user_{x}")
    email = factory.sequence(lambda x: f"user{x}@email.com")
    password = 'pass'
    is_verified = True
