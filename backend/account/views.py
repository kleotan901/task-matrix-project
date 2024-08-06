from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from account.serializers import UserSerializer, UserDetailSerializer, UserListSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserDetailSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserDetailSerializer
        return UserSerializer

    @extend_schema(
        description="Retrieve the authenticated user's details.",
        responses={200: UserDetailSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Update the authenticated user's details and/or change the password.",
        request=UserSerializer,
        responses={200: UserSerializer}
    )
    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description="Partially update the authenticated user's details.",
        request=UserListSerializer,
        responses={200: UserListSerializer}
    )
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
