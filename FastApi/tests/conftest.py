from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.main import app
from app.config import settings
from app.database import get_db
from app.database import Base
from app.oauth2 import create_access_token
from app import models
from alembic import command


# creating connection with base
#SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:password123@localhost:5432/fastapi_test'
SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}/{settings.database_name}_test'

#creating engine string
engine = create_engine(SQLALCHEMY_DATABASE_URL)

#creating session with data base
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


#testing function for creating and droping data base with each test (actual data base)
@pytest.fixture()
def session():
    #drop database
    Base.metadata.drop_all(bind=engine)
    #create database
    Base.metadata.create_all(bind=engine)

    # Going to create a session towards database for every request
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


#passing sesstion(database) to override data base
@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    #over rides all get_db into override_get_db
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app) 


@pytest.fixture
def test_user(client):
    user_data = {"email": "hello123@gmail.com", "password": "password123"}
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201
    new_user= res.json()
    new_user['password'] = user_data ['password']
    return new_user


@pytest.fixture
def token(test_user):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client


@pytest.fixture
def test_posts(test_user, session):
    posts_data = [{
        "title": "first title",
        "content": "first content",
        "owner_id": test_user['id']
    },{
        "title": "2nd title",
        "content": "2nd content",
        "owner_id": test_user['id']
    },{
        "title": "3rd title",
        "content": "3rd content",
        "owner_id": test_user['id']
    }]

    def create_post_model(post):
        return models.Post(**post)

    post_map = map(create_post_model, posts_data)
    posts = list(post_map)

    session.add_all(posts)
    # session.add_all([models.Post(title="first title", content="first content", owner_id = test_user['id']),
    #                  models.Post(title="2nd title", content="2nd content", owner_id =  test_user['id']),
    #                  models.Post(title="3nd title", content="3nd content", owner_id =  test_user['id'])])
    session.commit()

    posts = session.query(models.Post).all()
    return posts


