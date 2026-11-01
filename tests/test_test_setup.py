def test_test_database_is_available(db):
    assert db is not None


def test_student_fixture(student_user):
    assert student_user.username == "teststudent"
    assert student_user.role == "regular_user"


def test_admin_fixture(admin_user):
    assert admin_user.username == "testadmin"
    assert admin_user.role == "admin"


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"ok": True}
