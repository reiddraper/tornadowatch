import time

import tornado.web
import tornado.httpclient
import tornado.ioloop

class BaseHandler(tornado.web.RequestHandler):
    @property
    def subscribers(self):
        return self.application.subscribers

    @property
    def timeouts(self):
        return self.application.timeouts

class SubscribeHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self, resource):
        self.resource = resource
        self.subscribers[self.resource].add(self.on_response) 
        #set a timeout in case nothing is ever published
        loop = tornado.ioloop.IOLoop.instance()
        # TODO: don't hardcode the timeout
        deadline = time.time() + (60 * 10)
        timeout = loop.add_timeout(deadline, self.on_timeout) 
        self.timeouts[self.resource].add(timeout)
    
    def on_timeout(self):
        try:
            self.write('timeout')
        except IOError:
            pass
        # clear the subscribers and timeouts
        self.subscribers[self.resource] = set()
        self.timeouts[self.resource]    = set()
        self.finish()

    def on_response(self, response):
        loop = tornado.ioloop.IOLoop.instance()
        timeouts = self.timeouts[self.resource]
        self.timeouts[self.resource]    = set()
        for timeout in timeouts:
            loop.remove_timeout(timeout)

        self.set_header("Cache-Control", "no-store")
        self.write(response)
        self.finish()


class PublishHandler(BaseHandler):
    def post(self, resource):
        subscribers = self.subscribers[resource]
        content = self.request.body

        for subscriber in subscribers:
            try:
                subscriber(content)
            except IOError:
                pass

        # clear the subscribers
        self.subscribers[resource] = set()
