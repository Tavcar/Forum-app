#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import jinja2
import webapp2
from google.appengine.api import users
from models import Post
from models import Topic
from models import User
from operator import attrgetter
from datetime import datetime
from admins import ADMIN

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            logiran = True
            logout_url = users.create_logout_url('/')
            user = users.get_current_user()
            if user.nickname() in ADMIN:
                user.admin = True

            seznam = Topic.query().fetch()
            urejen = sorted(seznam, key=attrgetter("date"), reverse=True)
            params = {"logiran": logiran, "logout_url": logout_url, "user": user, "seznam": urejen}

        else:
            logiran = False
            login_url = users.create_login_url('/')
            params = {"logiran": logiran, "login_url": login_url, "user": user}

        return self.render_template("base.html", params=params)


class NewTopicHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        if user.nickname() in ADMIN:
            user.admin = True

        params = {"user": user}
        return self.render_template("new_topic.html", params=params)

    def post(self):

        user = users.get_current_user()
        name = user.nickname()
        title = self.request.get("title")
        content = self.request.get("content")
        date = datetime.now().strftime("%d-%m-%Y at %H:%M")

        topic = Topic.create(name, title, content, date)
        topic.put()

        return self.redirect('/topic/' + str(topic.key.id()))


class TopicHandler(BaseHandler):
    def get(self, topic_id):
        user = users.get_current_user()
        if user.nickname() in ADMIN:
            user.admin = True

        topic = Topic.get_by_id(int(topic_id))
        seznam = Post.query(Post.id_topic == int(topic_id)).fetch()

        urejen = sorted(seznam, key=attrgetter("date"), reverse=False)
        params = {"seznam": urejen, "topic": topic, "user": user}

        return self.render_template("topic1.html", params=params)

    def post(self, topic_id):
        user = users.get_current_user()
        name = user.nickname()
        content = self.request.get("content")
        date = datetime.now().strftime("%d-%m-%Y at %H.%M.%S")

        new_post = self.request.get("new-post")

        if new_post:
            if content:
                post = Post.create(name, content, int(topic_id), date)
                Topic.new_post(int(topic_id))

                topic = Topic.get_by_id(int(topic_id))
                return self.redirect('/topic/' + str(topic_id))
            else:
                return self.redirect('/topic/' + str(topic_id))


class DeleteTopicHandler(BaseHandler):
    def get(self, topic_id):
        user = users.get_current_user()
        if user.nickname() in ADMIN:
            user.admin = True

        return self.render_template("delete.html")

    def post(self, topic_id):
        topic = Topic.get_by_id(int(topic_id))
        topic.key.delete()

        return self.redirect_to("home")


class DeletePostHandler(BaseHandler):
    def get(self, post_id):
        user = users.get_current_user().nickname()

        if user in ADMIN or user == Post.get_by_id(int(post_id)).name:
            return self.render_template("delete.html")

    def post(self, post_id):
        post = Post.get_by_id(int(post_id))
        post.key.delete()

        return self.redirect("/topic/" + str(post.id_topic))


class CloseTopicHandler(BaseHandler):
    def get(self, topic_id):
        user = users.get_current_user()
        topic = Topic.get_by_id(int(topic_id))
        params = {"topic": topic, "user": user}

        if user.nickname() in ADMIN:
            user.admin = True
        return self.render_template("close.html", params=params)

    def post(self, topic_id):
        topic = Topic.get_by_id(int(topic_id))

        if topic.closed == False:
            topic.closed = True
            topic.put()
            return self.redirect('/topic/' + str(topic.key.id()))

        if topic.closed == True:
            topic.closed = False
            topic.put()
            return self.redirect('/topic/' + str(topic.key.id()))


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name="home"),
    webapp2.Route('/new-topic', NewTopicHandler),
    webapp2.Route('/topic/<topic_id:\d+>', TopicHandler, name="topic"),
    webapp2.Route('/delete-topic/<topic_id:\d+>', DeleteTopicHandler),
    webapp2.Route('/delete-post/<post_id:\d+>', DeletePostHandler),
    webapp2.Route('/close-open/<topic_id:\d+>', CloseTopicHandler),
], debug=True)
