def auth(client, user):
    logout(client)
    token = 'Bearer ' + user.get_auth_token()
    client.environ_base['authentication_token'] = token
    with client.session_transaction() as session:
        session['_user_id'] = str(user.id)
        session['_fresh'] = True


def logout(client):
    client.environ_base.pop('authentication_token', None)
    return client.get("/logout")
