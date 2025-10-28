import pytest
from fastapi.testclient import TestClient
from blog_crud.main import app
from blog_crud.schema import BlogRequest, CommentRequest

# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------
@pytest.fixture(scope="module")
def client():
    # lifespan context triggers DB connect/disconnect
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def signup_and_login(client):
    """Create a user and return their access token."""
    username = "tester"
    password = "secret"

    # sign up (ignore if already exists)
    client.post("/signup", json={"name": username, "password": password})

    # login to get JWT token
    resp = client.post("/login", data={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# -----------------------------------------------------------------------------
# Tests: Users
# -----------------------------------------------------------------------------
def test_signup_new_user(client):
    resp = client.post("/signup", json={"name": "unique_user", "password": "pw"})
    assert resp.status_code in (200, 403)  # user may already exist

def test_login_returns_token(client):
    client.post("/signup", json={"name": "tester", "password": "secret"})
    resp = client.post("/login", data={"username": "tester", "password": "secret"})
    assert resp.status_code == 200, resp.text
    assert "access_token" in resp.json()
# -----------------------------------------------------------------------------
# Tests: Blogs
# -----------------------------------------------------------------------------
def test_create_blog(client, signup_and_login):
    payload = BlogRequest(title="title one", content="content one").model_dump()
    resp = client.post("/blog", headers=signup_and_login, json=payload)
    assert resp.status_code == 200, resp.text

def test_get_all_blogs(client, signup_and_login):
    resp = client.get("/blogs", headers=signup_and_login)
    assert resp.status_code == 200
    data = resp.json()
    assert "blogs" in data

def test_get_blog_by_id(client, signup_and_login):
    # create a blog first
    new_blog = BlogRequest(title="temp", content="temp").model_dump()
    create_resp = client.post("/blog", headers=signup_and_login, json=new_blog)
    assert create_resp.status_code == 200
    # read blogs to get an ID
    list_resp = client.get("/blogs", headers=signup_and_login)
    blog_id = list_resp.json()["blogs"][0]["id"]
    resp = client.get(f"/blog/{blog_id}", headers=signup_and_login)
    assert resp.status_code == 200

def test_delete_blog(client, signup_and_login):
    # make a new blog, then delete it
    blog = BlogRequest(title="delete me", content="soon gone").model_dump()
    create_resp = client.post("/blog", headers=signup_and_login, json=blog)
    assert create_resp.status_code == 200
    blogs_resp = client.get("/blogs", headers=signup_and_login)
    blog_id = blogs_resp.json()["blogs"][-1]["id"]
    resp = client.delete(f"/blog/{blog_id}", headers=signup_and_login)
    assert resp.status_code == 200

# -----------------------------------------------------------------------------
# Tests: Comments
# -----------------------------------------------------------------------------
def test_add_comment_and_fetch(client, signup_and_login):
    # create a blog to comment on
    blog = BlogRequest(title="comment target", content="stuff").model_dump()
    client.post("/blog", headers=signup_and_login, json=blog)
    blogs_resp = client.get("/blogs", headers=signup_and_login)
    blog_id = blogs_resp.json()["blogs"][-1]["id"]

    # add comment
    comment_payload = CommentRequest(blog_id=blog_id, content="nice!").model_dump()
    resp = client.post("/comment", headers=signup_and_login, json=comment_payload)
    assert resp.status_code == 200

    # fetch comments for that blog
    resp = client.get(f"/blog/comments/{blog_id}", headers=signup_and_login)
    assert resp.status_code == 200
    assert "comments" in resp.json()

def test_user_comments_endpoint(client, signup_and_login):
    resp = client.get("/user/comments", headers=signup_and_login)
    assert resp.status_code == 200
