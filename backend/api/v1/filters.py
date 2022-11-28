from django_filters.rest_framework import (BooleanFilter, CharFilter,
                                           FilterSet,
                                           ModelMultipleChoiceFilter)
from recipes.models import Recipe, Tag
from rest_framework.filters import SearchFilter


class IngredientFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(FilterSet):
    author = CharFilter(field_name='author__id',)
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = BooleanFilter(method='favorited_filter')
    is_in_shopping_cart = BooleanFilter(method='shopping_cart_filter')

    def favorited_filter(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(is_favorited__author=user)
        return queryset

    def shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(is_in_shopping_cart__author=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited')
