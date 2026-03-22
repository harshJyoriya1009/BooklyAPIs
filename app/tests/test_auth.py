auth_prefix = f"/api/v1/auth"

def test_user_creation(fake_session, fake_user_service, test_client):
    signup_data ={
            "username": "Harsh Jyoriya",
            "email": "harshjyoriya639khhk@gmail.com",
            "password": "facebookmetas"  
    }
    response = test_client.post(
        url=f"{auth_prefix}/register",
        json=signup_data

    )
    assert fake_user_service.user_exists_called_once()