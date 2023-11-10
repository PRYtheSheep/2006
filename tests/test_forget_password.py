def forget_password_request(client):
    response = client.post('/forgetpassword', data={
        "email": "test@test.com"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'A password reset link has been sent to your email' in response.data

def forget_password_request_wrong_email(client):
    response = client.post('/forgetpassword', data={
        "email": "testtest.com"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'There are no accounts with this email' in response.data

def forget_password_request_exceed_limit(client):
    response = client.post('/forgetpassword', data={
        "email": "test2@test.com"
    }, follow_redirects=True)

    response = client.post('/forgetpassword', data={
        "email": "test2@test.com"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'You have requested a password reset in the last 5 minutes. Please try again later.' in response.data
