from microblog_api.models import Post, User, Tag, Rating, db


tag1, tag2, tag3 = '#tag1', '#tag2', '#tag3'


async def test_create_tags_with_existing(client):
    await Tag.create(name=tag1)
    await Tag.create(name=tag2)
    await Tag.create(name=tag3)
    new_tags = [tag1, tag2, 'tag4', '#tag5', 'tag6', None, '']
    result = await Tag.create_all(new_tags)
    assert len(result) == 5


async def test_create_empty(client):
    new_tags = [tag1, tag2, 'tag4', '#tag5', 'tag6', None, '']
    result = await Tag.create_all(new_tags)
    assert len(result) == 5


async def test_create_existing(client):
    await Tag.create(name=tag1)
    await Tag.create(name=tag2)
    await Tag.create(name=tag3)
    new_tags = [tag1, tag2, tag3]
    result = await Tag.create_all(new_tags)
    assert len(result) == 3

