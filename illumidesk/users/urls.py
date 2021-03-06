from django.urls import path

from illumidesk.users.views import user_detail_view
from illumidesk.users.views import user_redirect_view
from illumidesk.users.views import user_update_view

from . import views


app_name = 'users'
urlpatterns = [
    path(r'profile/', views.profile, name='user_profile'),
    path(r'profile/upload-image/', views.upload_profile_image, name='upload_profile_image'),
]
