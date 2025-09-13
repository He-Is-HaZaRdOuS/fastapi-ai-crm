from string import ascii_letters, digits
import re

# import toml

# # Load configs from config files
# with open('configuration/reserved_usernames.toml', 'r') as file_reserved:
#     config_reserved = toml.load(file_reserved)

# with open('configuration/elevated_users.toml', 'r') as file_elevated:
#     config_elevated = toml.load(file_elevated)

# reserved_usernames = config_reserved['users']['reserved_usernames']
# elevated_users = config_elevated['users']['elevated_users']

# reserved_usernames = reserved_usernames + elevated_users


def password_is_valid(password):
    if len(password) < 8:
        return False
    if not any(ele.isupper() for ele in password):
        return False
    if not any(ele.islower() for ele in password):
        return False
    if not any(ele.isdigit() for ele in password):
        return False
    if not set(password).difference(ascii_letters + digits):
        return False
    return True

def email_is_valid(email: str) -> bool:
    # Basic sanity checks
    if not (5 <= len(email) <= 254):
        return False

    # RFC 5322
    pattern = re.compile(
        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )
    if not pattern.match(email):
        return False

    # Prevent multiple @
    if email.count("@") != 1:
        return False

    local, domain = email.rsplit("@", 1)

    # Extra checks
    if local.startswith(".") or local.endswith("."):
        return False
    if ".." in local or ".." in domain:
        return False
    if domain.startswith("-") or domain.endswith("-"):
        return False

    return True


# def username_is_valid(username):
#     if not(4 <= len(username) <= 12):
#         return False
#     if not username.isalnum():
#         return False
#     if username.lower() != username:
#         return False
#     return True

# def username_is_reserved(username):
#     return username in reserved_usernames
