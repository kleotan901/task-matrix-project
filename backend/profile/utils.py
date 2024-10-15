from profile.models import User


def split_full_name(user: User, full_name: str) -> User:
    user.first_name = full_name.split()[0]
    if len(full_name.split()) > 1:
        user.last_name = " ".join(full_name.split()[1:])
    user.save()
    return user
