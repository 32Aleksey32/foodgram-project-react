import io

from django.db.models.aggregates import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            Subscribe, Tag)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status, views, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import User

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeReadSerializer, SubscribeSerializer,
                          TagSerializer, TokenSerializer, UniversalSerializer,
                          UserCreateSerializer, UserSerializer)

FILENAME = 'shopping_cart.pdf'


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='subscribe',
        permission_classes=[IsAuthenticatedOrReadOnly],
    )
    def subscribe(self, request, id=None):
        user = get_object_or_404(User, id=id)
        subscribe = Subscribe.objects.filter(
            user=request.user,
            author=user
        )
        if request.method == 'POST':
            if user == request.user:
                msg = {'error': 'Нельзя подписаться на самого себя.'}
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)
            obj, created = Subscribe.objects.get_or_create(
                user=request.user,
                author=user
            )
            if not created:
                msg = {'error': 'Вы уже подписаны на этого пользователя.'}
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscribeSerializer(obj, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not subscribe.exists():
            msg = {'error': 'Вы не подписаны на этого пользователя.'}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticatedOrReadOnly],
    )
    def subscriptions(self, request):
        pages = self.paginate_queryset(
            Subscribe.objects.filter(user=request.user)
        )
        serializer = SubscribeSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TokenView(views.APIView):
    serializer_class = TokenSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            email=serializer.validated_data.get('email'),
            password=serializer.validated_data.get('password')
        )
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH', 'PUT']:
            return RecipeCreateSerializer
        return RecipeReadSerializer

    def add_recipe(self, model, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        models = model.objects.filter(author=request.user, recipe=recipe)
        if models.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        model(author=request.user, recipe=recipe).save()
        serializer = UniversalSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def del_recipe(self, model, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        models = model.objects.filter(author=request.user, recipe=recipe)
        if models.exists():
            models.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='favorite',
        permission_classes=[IsAuthenticatedOrReadOnly]
    )
    def favorite(self, request, **kwargs):
        if request.method == 'POST':
            return self.add_recipe(FavoriteRecipe, request, kwargs.get('pk'))
        if request.method == 'DELETE':
            return self.del_recipe(FavoriteRecipe, request, kwargs.get('pk'))

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
        permission_classes=[IsAuthenticatedOrReadOnly]
    )
    def shopping_cart(self, request, **kwargs):
        if request.method == 'POST':
            return self.add_recipe(ShoppingCart, request, kwargs.get('pk'))
        if request.method == 'DELETE':
            return self.del_recipe(ShoppingCart, request, kwargs.get('pk'))

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        buffer = io.BytesIO()
        page = canvas.Canvas(buffer)
        pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
        x_position, y_position = 50, 800
        shopping_cart = (
            request.user.is_in_shopping_cart.recipe.
            values(
                'ingredients__name',
                'ingredients__measurement_unit'
            ).annotate(amount_ingredients=Sum('recipe__amount')).order_by())
        page.setFont('Vera', 14)
        if shopping_cart:
            indent = 20
            page.drawString(x_position, y_position, 'Список покупок:')
            for index, recipe in enumerate(shopping_cart, start=1):
                page.drawString(
                    x_position, y_position - indent,
                    f'{index}. {recipe["ingredients__name"]} - '
                    f'{recipe["amount"]} '
                    f'{recipe["ingredients__measurement_unit"]}.')
                y_position -= 15
                if y_position <= 50:
                    page.showPage()
                    y_position = 800
            page.save()
            buffer.seek(0)
            return FileResponse(buffer, as_attachment=True, filename=FILENAME)
        page.setFont('Vera', 24)
        page.drawString(x_position, y_position, 'Список покупок пуст!')
        page.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=FILENAME)
