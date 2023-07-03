# ---------- Python's Libraries ---------------------------------------------------------------------------------------

# ---------- Django Tools Rest Framework, Oauth 2 Tools ---------------------------------------------------------------
from django.urls import path, include
# from django.views.generic import TemplateView

import oauth2_provider.views as oauth2_views

# ---------- Created Tools --------------------------------------------------------------------------------------------
# from apis.views.v1 import noti
from apis.views.v1 import user, auth

oauth2_endpoint_views = (
    [
        path('authorize/', oauth2_views.AuthorizationView.as_view(), name='authorize'),
        path('token/', auth.ApiEndpoint.as_view(), name='token'),
        path('revoke-token/', oauth2_views.RevokeTokenView.as_view(), name='revoke-token'),
        path('applications/', oauth2_views.ApplicationList.as_view(), name='list'),
        path('applications/register/', oauth2_views.ApplicationRegistration.as_view(), name='register'),
        path('applications/<pk>/', oauth2_views.ApplicationDetail.as_view(), name='detail'),
        path('applications/<pk>/delete/', oauth2_views.ApplicationDelete.as_view(), name='delete'),
        path('applications/<pk>/update/', oauth2_views.ApplicationUpdate.as_view(), name='update'),
        path('authorized-tokens/', oauth2_views.AuthorizedTokensListView.as_view(), name='authorized-token-list'),
        path('authorized-tokens/<pk>/delete/', oauth2_views.AuthorizedTokenDeleteView.as_view(),
             name='authorized-token-delete')
    ], 'oauth2_provider')


urlpatterns = [
    path('o/', include(oauth2_endpoint_views)),
]
