from .views import unread_count_for_user


def messaging_unread_count(request):
    return {'messaging_unread_count': unread_count_for_user(request.user)}
