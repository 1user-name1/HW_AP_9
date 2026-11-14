from typing import List

# ключи пока просто тут лежат, по хорошему надо в базе хранить
API_KEYS = {
    'reader-key': {'uid': 'reader', 'role': 'reader'},
    'admin-key': {'uid': 'librarian', 'role': 'librarian'},
}


def info_from_ApiKeyAuth(api_key, required_scopes):
    """
    Check and retrieve authentication information from api_key.
    Returned value will be passed in 'token_info' parameter of your operation function, if there is one.
    'sub' or 'uid' will be set in 'user' parameter of your operation function, if there is one.

    :param api_key API key provided by Authorization header
    :type api_key: str
    :param required_scopes Always None. Used for other authentication method
    :type required_scopes: None
    :return: Information attached to provided api_key or None if api_key is invalid or does not allow access to called API
    :rtype: dict | None
    """
    # если ключа нет в словаре то вернется None и connexion сам отдаст 401
    return API_KEYS.get(api_key)
