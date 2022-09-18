from django.urls import path
from .views import HomePage, UpdateTask, Login, Register, Logout, DeleteTask, DashBoard, DeleteUser, Notify, password_reset_request, UpdateProfile
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', HomePage, name='home'),
    path('update/<int:id>/', UpdateTask, name='update-task'),
    path('login/', Login, name='login'),
    path('register/', Register, name='register'),
    path('logout/', Logout, name='logout'),
    path('delete/<int:id>/', DeleteTask, name='delete-task'),
    path('dashboard/', DashBoard, name='dash'),
    path('dashboard/delete-user/', DeleteUser, name='delete-user'),
    path('dashboard/notify', Notify, name='notify'),
    path('update_profile/<int:id>/', UpdateProfile, name='update-profile'),

    path('reset_password/', password_reset_request, name="reset_password"),

    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="td/password_reset_sent.html"), name="password_reset_done"),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="td/password_reset_form.html"), name="password_reset_confirm"),

    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="td/password_reset_done.html"), name="password_reset_complete"),
]