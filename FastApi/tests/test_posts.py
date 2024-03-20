import pytest
from app import schemas


#test geting all posts
def test_get_all_posts(authorized_client, test_posts):
    res = authorized_client.get("/posts/")

    # #converting into list
    # def validate(post):
    #     return schemas.PostOut(**post)
    # posts_map = map(validate, res.json())
    # posts = list(posts_map)
    # assert posts_list[0].Post.id == test_posts[0].id

    print(res.json())
    assert len(res.json()) == len(test_posts)
    assert res.status_code == 200


#test if unauthorized person get all posts
def test_unathorizer_user_get_all_posts(client, test_posts):
    res = client.get("/posts/")
    assert res.status_code == 401


#test if unauthorized person get one post
def test_unathorizer_user_get_one_posts(client, test_posts):
    res = client.get(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401


#test get one post not exist
def test_unathorizer_user_get_not_exist(authorized_client, test_posts):
    res = authorized_client.get("/posts/999999")
    assert res.status_code == 404


#test get one post
def test_get_one_post(authorized_client, test_posts):
    res= authorized_client.get(f"/posts/{test_posts[0].id}")

    post = schemas.PostOut(**res.json())
    assert post.Post.id == test_posts[0].id
    assert post.Post.content == test_posts[0].content


#test creating a new post by authorized user
@pytest.mark.parametrize("title, content, published",[
    ("awesome new title", "awesome new content", True),
    ("favorite pizza", "SRBIJANAAA", False),
    ("something to try", "tru to something", True),
])
def test_create_post(authorized_client, test_user, test_posts, title, content,published):
    res = authorized_client.post("/posts/", json={"title": title, "content": content, "published": published})

    created_post = schemas.PostResponse(**res.json())
    assert res.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.owner_id == test_user['id']


#test_published_true
def test_create_post_default_published_true(authorized_client, test_user, test_posts):
    res = authorized_client.post("/posts/", json={"title": "some test title", "content": "content"})

    created_post = schemas.PostResponse(**res.json())
    assert res.status_code == 201
    assert created_post.title == "some test title"
    assert created_post.content == "content"
    assert created_post.published == True
    assert created_post.owner_id == test_user['id']


#test unauthorized user create post
def test_unathorizer_user_create_post(client, test_posts, test_user):
    res = client.post("/posts/", json={"title": "some test title", "content": "content"})
    assert res.status_code == 401


#test unauthorized user delete post
def test_unauthorized_user_delete_post(client, test_user, test_posts):
    res = client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401


#test authorized user delete post
def test_delete_post_success(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 204


#test deleteing non existing post
def test_delete_post_non_exist(authorized_client, test_user, test_posts):
    res = authorized_client.delete("/posts/99999")
    assert res.status_code == 404


#test one user deleting post of another user
def test_delete_other_user_post(authorized_client, test_posts, test_user):
    res = authorized_client.delete(f"/posts/{test_posts[3].id}")
    assert res.status_code == 403


#test update post
def test_update_post(authorized_client, test_posts, test_user):
    data={
        "title": "updated title",
        "content": "updated content",
        "id": test_posts[0].id 
    }
    
    res = authorized_client.put(f"/posts/{test_posts[0].id}", json=data)
    updated_post = schemas.PostResponse(**res.json())
    assert res.status_code == 200
    assert updated_post.title == data["title"]
    assert updated_post.content == data ["content"]


#test update post of other user
def test_update_other_user_post(authorized_client, test_posts, test_user, test_user2):
    data={
        "title": "updated title",
        "content": "updated content",
        "id": test_posts[3].id 
    }
    res = authorized_client.put(f"/posts/{test_posts[3].id}", json=data)
    assert res.status_code == 403


#test unauthorized user update post
def test_unauthorized_user_update_post(client, test_user, test_posts):
    res = client.put(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401


#test updateing non existing post
def test_update_post_non_exist(authorized_client, test_user, test_posts):
    data={
        "title": "updated title",
        "content": "updated content",
        "id": test_posts[3].id 
    }
    res = authorized_client.put("/posts/99999", json=data)

    assert res.status_code == 404