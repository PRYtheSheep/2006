def test_get_property_page_not_logged_in(client):
    response = client.get('/map/property/1', follow_redirects=True)

    assert response.status_code == 200
    assert b"Please login to access this page." in response.data
    
def test_get_routes_property_1_success(client):
    response = client.post('/login', data={
        "email": "test@test.com",
        "password": "123456789aA$"
    }, follow_redirects=True)

    response = client.post('/map/1', data={
        "target_location": "80 PUNGGOL FIELD PUNGGOL 21 COMMUNITY CLUB SINGAPORE 828815",
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Route 1" in response.data

def test_get_routes_property_1_error(client):
    response = client.post('/login', data={
        "email": "test@test.com",
        "password": "123456789aA$"
    }, follow_redirects=True)

    response = client.post('/map/1', data={
        "target_location": "dfghdfhfghfg",
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid address, please select another address." in response.data
    
