from profile.models import User


def split_full_name(user: User, full_name: str) -> User:
    if not full_name:
        user.first_name = None
        user.last_name = None
    elif len(full_name.split()) > 1:
        user.first_name = full_name.split()[0]
        user.last_name = " ".join(full_name.split()[1:])
    else:
        user.first_name = full_name.split()[0]
        user.last_name = None
    user.save()
    return user
