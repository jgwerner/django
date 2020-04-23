from django.urls import path

from . import views


app_name = 'subscriptions'
urlpatterns = [

    # team-specific URLs
    # todo: it would be better if these matched the /a/team-slug/subscription pattern of other pages
    path('team/<slug:team_slug>/', views.team_subscription, name='team_subscription_details'),
    path('team/<slug:team_slug>/subscription_success/',
         views.team_subscription_success, name='team_subscription_success'),
    path('team/<slug:team_slug>/demo/',
         views.team_subscription_demo, name='team_subscription_demo'),
    path('team/<slug:team_slug>/subscription-gated-page/',
         views.team_subscription_gated_page, name='team_subscription_gated_page'),
    path('team/<slug:team_slug>/api/create_customer/',
         views.team_create_customer, name='team_create_customer'),
]
