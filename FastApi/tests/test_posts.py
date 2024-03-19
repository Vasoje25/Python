from typing import List
from app import schemas


#creating test for geting all posts
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


#TODO 16:51:00