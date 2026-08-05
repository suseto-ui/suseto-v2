def list_users():
    return []


def create_user(username, password, role='viewer'):
    return {'username': username, 'role': role, 'active': True}


def set_role(username, role='viewer'):
    return {'username': username, 'role': role}


def toggle_active(username):
    return {'username': username, 'active': True}


def verify(username, password):
    if username:
        return {'username': username, 'role': 'viewer'}
    return None


def delete_user(username):
    return {'username': username, 'deleted': True}


def reset_password(username, new_password):
    return {'username': username, 'reset': True}


def change_password(username, old_password, new_password):
    return {'username': username, 'changed': True}
