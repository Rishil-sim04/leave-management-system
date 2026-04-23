from django.urls import path
from .views import (
    LeaveListCreateView,
    LeaveDetailView,
    ApplyOnBehalfView,
    LeaveBalanceView,
    HolidayListView,
    CustomNotifyListView,
    LeaveBalanceManageView
)

urlpatterns = [
    path('', LeaveListCreateView.as_view(), name='leave-list-create'),
    path('<int:leave_id>/', LeaveDetailView.as_view(), name='leave-detail'),
    path('behalf/<int:emp_id>/', ApplyOnBehalfView.as_view(), name='apply-on-behalf'),
    path('balance/', LeaveBalanceView.as_view(), name='leave-balance'),
    path('holidays/', HolidayListView.as_view(), name='holiday-list'),
    path('notify/', CustomNotifyListView.as_view(), name='notify-list'),
    path('notify/<int:notify_id>/', CustomNotifyListView.as_view(), name='notify-delete'),
    path('balance/manage/', LeaveBalanceManageView.as_view(), name='leave-balance-manage'),
]



 

 
 