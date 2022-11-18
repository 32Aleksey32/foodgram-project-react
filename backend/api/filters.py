from django_filters.rest_framework import (AllValuesMultipleFilter,
                                           BooleanFilter, CharFilter,
                                           FilterSet, ModelChoiceFilter)
from recipes.models import Ingredient, Recipe, User


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    tags = AllValuesMultipleFilter(
        field_name='tags__slug',
        label='Тег'
    )
    author = ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = BooleanFilter(label='В избранных.')
    is_in_shopping_cart = BooleanFilter(label='В корзине.')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')
