from google.appengine.ext import ndb

class Topic(ndb.Model):
    name = ndb.StringProperty()
    title = ndb.StringProperty()
    date = ndb.StringProperty()
    content = ndb.StringProperty()
    closed = ndb.BooleanProperty(default=False)


    @classmethod
    def create(cls, name, title, content, date):
        topic = cls(name=name, title=title, content=content, date=date)
        topic.put()
        return topic

    @classmethod
    def new_post(cls, topic_id):
        topic = Topic.get_by_id(topic_id)
        topic.put()


class Post(ndb.Model):
    name = ndb.StringProperty()
    content = ndb.StringProperty()
    date = ndb.StringProperty()
    id_topic = ndb.IntegerProperty()

    @classmethod
    def create(cls, name, content, topic_id, date):
        post = cls(name=name, content=content, id_topic=topic_id, date=date)
        post.put()
        return post


class User(ndb.Model):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    admin = ndb.BooleanProperty(default=False)

    @classmethod
    def create(cls, email, admin):
        user = cls(email=email, admin=admin)
        user.put()
        return user
