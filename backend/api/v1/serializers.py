from drf_base64.fields import Base64ImageField
from recipes.models import (Ingredient, IngredientInRecipe, Recipe, Subscribe,
                            Tag)
from rest_framework.serializers import (CharField, EmailField, IntegerField,
                                        ModelSerializer, ReadOnlyField,
                                        SerializerMethodField, ValidationError)
from users.models import User


class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return user.subscriber.filter(author=obj).exists()


class UserCreateSerializer(ModelSerializer):
    """Позволяет зарегистрироваться новому пользователю."""
    password = CharField(
        label='Пароль',
        required=True,
        style={'input_type': 'password'}
    )
    email = EmailField(label='Адрес электронной почты', required=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'password',
        )

    def validate_email(self, data):
        if User.objects.filter(email=data).exists():
            raise ValidationError(
                "Пользователь с таким адресом эл. почты уже существует."
            )
        return data

    def validate_username(self, data):
        if User.objects.filter(username=data).exists():
            raise ValidationError(
                "Пользователь с таким юзернеймом уже существует."
            )
        return data

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


# class TokenSerializer(Serializer):
#     email = CharField(
#         label='Электронная почта',
#         required=True,
#     )
#     password = CharField(
#         label='Пароль',
#         style={'input_type': 'password'}
#     )


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(ModelSerializer):
    id = IngredientSerializer()
    name = CharField(required=False)
    measurement_unit = IntegerField(required=False)
    amount = IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def to_representation(self, instance):
        data = IngredientSerializer(instance.ingredient).data
        data['amount'] = instance.amount
        return data


class RecipeReadSerializer(ModelSerializer):
    author = UserSerializer(many=False, read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientInRecipeSerializer(many=True, source='recipe')
    image = Base64ImageField()
    is_favorited = SerializerMethodField(
        read_only=True,
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = SerializerMethodField(
        read_only=True,
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'name', 'author', 'ingredients', 'image', 'text',
            'cooking_time', 'is_favorited', 'is_in_shopping_cart',
        )

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return recipe.is_favorited.filter(author=user).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return recipe.is_in_shopping_cart.filter(author=user).exists()


class RecipeCreateSerializer(ModelSerializer):
    ingredients = IngredientInRecipeSerializer(many=True, read_only=True)
    author = UserSerializer(many=False, read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time', 'author'
        )

    def validate(self, data):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        if not tags:
            raise ValidationError('Добавьте хотя бы один тег')
        if not ingredients:
            raise ValidationError('Добавьте хотя бы один ингредиент.')
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredient_list:
                raise ValidationError('Ингредиент должен быть уникальным!')
            ingredient_list.append(ingredient_id)
            try:
                int(ingredient['amount'])
            except ValueError:
                raise ValidationError(
                    'Кол-во ингредиентов должно быть указано только цифрами.'
                )
            if int(ingredient['amount']) <= 0:
                raise ValidationError('Укажите вес/количество ингредиентов')
        return data

    def validate_name(self, name):
        if len(name) < 3:
            raise ValidationError(
                'Название рецепта должно содержать не менее 3 символов.'
            )
        name = name[0].upper() + name[1:]
        recipe = Recipe.objects.filter(
            author=self.context['request'].user,
            name=name
        ).exists()
        if recipe and self.context['request'].method == 'POST':
            raise ValidationError('Вы уже сохранили рецепт с таким названием.')
        return name

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) < 1:
            raise ValidationError('Время приготовления меньше 1!')
        return cooking_time

    def validate_text(self, text):
        if len(text) < 10:
            raise ValidationError(
                'Описание рецепта должно содержать не менее 10 символов.'
            )
        return text[0].upper() + text[1:]

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientInRecipe(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient.get('amount')
            ).save()

    def create(self, validated_data):
        ingredients = self.initial_data.get('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, recipe, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            recipe.ingredients.clear()
            self.create_ingredients(ingredients, recipe)
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            recipe.tags.set(tags)
        return super().update(recipe, validated_data)


class UniversalSerializer(ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(UserSerializer):
    id = ReadOnlyField(source='author.id')
    username = ReadOnlyField(source='author.username')
    first_name = ReadOnlyField(source='author.first_name')
    last_name = ReadOnlyField(source='author.last_name')
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes',
        )

    def validate(self, attrs):
        user = self.initial_data.get('user')
        author = self.initial_data.get('author')
        if user == author:
            raise ValidationError('Нельзя подписаться на самого себя!')
        subscribed = Subscribe.objects.filter(user=user, author=author)
        if self.initial_data.get('method') == 'POST':
            if subscribed.exists():
                raise ValidationError('Вы уже подписаны на этого автора')
        else:
            if not subscribed.exists():
                raise ValidationError('Вы не подписаны на этого автора')
        return attrs

    def get_is_subscribed(self, username):
        return True

    def get_recipes(self, data):
        limit = self.context.get('request').query_params.get('recipes_limit')
        if not limit:
            limit = 3
        recipes = data.author.recipe.all()[:int(limit)]
        return UniversalSerializer(recipes, many=True).data
