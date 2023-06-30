from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet
from djoser.views import TokenCreateView, TokenDestroyView


app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/token/login/', TokenCreateView.as_view(),
         name='token_login'),
    path('auth/token/logout/', TokenDestroyView.as_view(),
         name='token_logout'),
]
urlpatterns+= router.urls