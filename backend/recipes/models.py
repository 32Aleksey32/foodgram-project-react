from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db.models import (CASCADE, CharField, DateTimeField, ForeignKey,
                              ImageField, ManyToManyField, Model,
                              PositiveSmallIntegerField, SlugField, TextField,
                              UniqueConstraint)

User = get_user_model()


class Ingredient(Model):
    name = CharField(
        'Наименование ингредиента',
        max_length=200,
        unique=True
    )
    measurement_unit = CharField(
        'Единица измерения',
        max_length=100
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}.'


class Tag(Model):
    name = CharField(
        'Наименование тега',
        max_length=200,
        unique=True
    )
    slug = SlugField(unique=True)
    color = ColorField(
        'Цветовой HEX-код',
        default='#FF0000',
        unique=True
    )

    class Meta:
        ordering = ['-name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = [
            UniqueConstraint(
                fields=['name', 'slug', 'color'],
                name='unique_tag'
            )
        ]

    def __str__(self):
        return self.name


class Recipe(Model):
    author = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='recipe',
        verbose_name='Автор рецепта'
    )
    name = CharField(
        'Наименование рецепта',
        max_length=200
    )
    image = ImageField(
        'Картинка',
        upload_to='recipes/',
        help_text='Загрузите картинку',
    )
    text = TextField('Описание рецепта')
    ingredients = ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='Ингредиент',
        verbose_name='Ингредиенты',
        help_text='Выберите ингредиенты для рецепта'
    )
    tags = ManyToManyField(
        Tag,
        related_name='recipe',
        verbose_name='Теги'
    )
    cooking_time = PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        default=0,
        validators=[MinValueValidator(1)]
    )
    pub_date = DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = (
            UniqueConstraint(
                fields=('author', 'name'),
                name='unique_recipe',
            ),
        )

    def __str__(self):
        return f'{self.name}'


class IngredientInRecipe(Model):
    amount = PositiveSmallIntegerField(
        'Количество в рецепте',
        default=0,
        validators=[MinValueValidator(1)]
    )
    ingredient = ForeignKey(
        Ingredient,
        on_delete=CASCADE,
        related_name='ingredient',
        verbose_name='Ингредиента в рецепте',
    )
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='recipe',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ['ingredient']
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'ingredient',),
                name='unique_ingredient_in_recipe',
            ),
        )

    def __str__(self):
        return f'{self.ingredient.name}'


class Subscribe(Model):
    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
    )
    author = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='subscribed',
        verbose_name='Автор',
    )
    pub_date = DateTimeField(
        'Дата подписки',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription')]

    def __str__(self):
        return f'{self.author}'


class FavoriteRecipe(Model):
    author = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='is_favorited',
        verbose_name='Владелец избранного',
    )
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='is_favorited',
        verbose_name='Избранный рецепт',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            UniqueConstraint(
                fields=('author', 'recipe'),
                name='unique_favorite')
        ]

    def __str__(self):
        recipe = [item['name'] for item in self.recipe.values('name')]
        return f'{recipe}'


class ShoppingCart(Model):
    author = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='is_in_shopping_cart',
        verbose_name='Владелец списка покупок',
    )
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='is_in_shopping_cart',
        verbose_name='Рецепт в списке покупок',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = (
            UniqueConstraint(
                fields=('author', 'recipe'),
                name='unique_shopping_cart',
            ),
        )

    def __str__(self):
        recipe = [item['name'] for item in self.recipe.values('name')]
        return f'{recipe}'
