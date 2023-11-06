from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path
from . views import( RegistrationAPIView, UserAPIView, 
                    FollowUserAPIView, UnfollowUserAPIView, ReviewAPIView, 
                    FollowersAPIView, FollowingAPIView,
                    )

urlpatterns = [
    # user endpoints
    path('user/me/', UserAPIView.as_view(), name='user'),
    path('user/follow/', FollowUserAPIView.as_view(), name='follow_user'),
    path('user/unfollow/', UnfollowUserAPIView.as_view(), name='unfollow_user'),
    path('user/review/', ReviewAPIView.as_view(), name='review_user'),
    path('user/followers/', FollowersAPIView.as_view(), name='followers'),
    path('user/following/', FollowingAPIView.as_view(), name='following'),

]