from http import HTTPStatus

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, views, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from reviews.models import Category, Comment, Genre, Review, Title, User

from .filters import FilterTitle
from .mixins import ListCreateDeleteViewSet
from .permissions import AdminRO, AdminSuperUser, AuthenticatedRO
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitlePostSerializer, TitleSerializer,
                          TokenCreateSerializer, UserSerializer,
                          UserSignUpSerializer)


class ReviewViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, AuthenticatedRO, )

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return Review.objects.filter(title=self.get_title().id)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AuthenticatedRO, )

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return Comment.objects.filter(review=self.get_review().id)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class CategoryViewSet(ListCreateDeleteViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination


class GenreViewSet(ListCreateDeleteViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitleSerializer
    filterset_class = FilterTitle
    search_fields = ('name', 'year', 'genre__slug', 'category__slug')
    permission_classes = (AdminRO, )
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    queryset = (Title.objects.annotate
                (rating=Avg('reviews__score')).order_by('name')
                )

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleSerializer
        return TitlePostSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, AdminSuperUser, )
    search_fields = ('username',)
    filter_backends = (filters.SearchFilter,)
    pagination_class = LimitOffsetPagination

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        url_name='me',
        permission_classes=(IsAuthenticated, )
    )
    def me(self, request):
        user = self.request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        serializer = self.get_serializer(user,
                                         data=request.data, partial=True)
        if request.method == "PATCH":
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data)
        return Response(serializer.data)


class TokenCreateViewSet(views.APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = TokenCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            data={'access': str(serializer.validated_data)},
            status=HTTPStatus.OK
        )


class UserSignUpViewSet(views.APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        if User.objects.filter(username=request.data.get('username'),
                               email=request.data.get('email')).exists():
            return Response(request.data, status=HTTPStatus.OK)
        serializer = UserSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = get_random_string(length=256)
        serializer.save(confirmation_code=confirmation_code)
        send_mail(
            'Confirmation code for Yamdb',
            f'Your confirmation code {confirmation_code}',
            settings.EMAIL_USER_SIGN,
            [serializer.validated_data['email']],
        )
        return Response(
            data=serializer.validated_data,
            status=HTTPStatus.OK
        )
