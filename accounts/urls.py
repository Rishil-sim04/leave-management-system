from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, PasswordChangeView, LogoutView, UpdateProfileView, EmployeeListView,

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password-change/', PasswordChangeView.as_view(), name='password_change'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UpdateProfileView.as_view(), name='update_own_profile'),
    path('profile/<int:emp_id>/', UpdateProfileView.as_view(), name='update_emp_profile'),
    path('employees/', EmployeeListView.as_view(), name='employee_list'),
]
 


 
