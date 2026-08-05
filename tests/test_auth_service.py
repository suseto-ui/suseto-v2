from services.auth_service import verify, list_users, create_user


def test_verify_returns_user_for_username():
    user = verify('admin', 'x')
    assert user is not None
    assert 'username' in user


def test_list_users_returns_list():
    users = list_users()
    assert isinstance(users, list)


def test_create_user_returns_username():
    user = create_user('alice', 'pw', 'viewer')
    assert user['username'] == 'alice'
