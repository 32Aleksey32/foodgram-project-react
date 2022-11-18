from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                    UserViewSet, TokenView)


app_name = 'api'

router = DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('auth/token/login', TokenView.as_view(), name='token'),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
