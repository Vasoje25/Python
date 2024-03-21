import pytest
from app import models


#creating alredy voted post
@pytest.fixture()
def test_vote(test_posts, session, test_user):
    new_vote = models.Vote(post_id = test_posts[3].id, user_id=test_user['id'])
    session.add(new_vote)
    session.commit()


#test vote post succes
def test_vote_on_post(authorized_client, test_posts):
    res = authorized_client.post("/vote/", json={"post_id": test_posts[0].id, "dir": 1})
    assert res.status_code == 201


#test vote alredy voted post
def test_vote_twice_post(authorized_client, test_posts, test_vote):
    res= authorized_client.post("/vote/", json={"post_id":test_posts[3].id, "dir": 1})
    assert res.status_code == 409


#test deleting vote
def test_delete_vote(authorized_client, test_posts, test_vote):
    res = authorized_client.post("/vote/", json={"post_id": test_posts[3].id, "dir": 0})
    assert res.status_code == 201


#test deleting vote from post that isnt liked
def test_detele_vote_non_exist(authorized_client, test_posts):
    res = authorized_client.post("/vote/", json={"post_id": test_posts[3].id, "dir": 0})
    assert res.status_code == 404


#test voting not existed post
def test_vote_post_non_exist(authorized_client, test_posts):
    res = authorized_client.post("/vote/", json={"post_id": 20000, "dir": 1})
    assert res.status_code == 404


#test unauthorized user vote
def test_vote_unauthorized_user(client, test_posts):
    res = client.post("/vote/", json={"post_id": test_posts[3].id, "dir": 1})
    assert res.status_code == 401