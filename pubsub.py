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
    def _cleanup(self):
        to_remove = self._get_subscription_key()
        try:
            self.subscribers[to_remove].remove(self._on_response)
        except KeyError:
            pass

    def on_connection_close(self):
        self._cleanup()

    @tornado.web.asynchronous
    def get(self, resource):
        # figure out if the connection should be closed
        # or not
        connection_header = self.request.headers.get('Connection', None)
        if connection_header == 'close':
            self._close_connection = True
        else:
            self._close_connection = False

        self.resource = resource
        self._add_subscriber()

        timeout_seconds = self._get_timeout()
        if timeout_seconds:
            #set a timeout in case nothing is ever published
            loop = tornado.ioloop.IOLoop.instance()
            deadline = time.time() + timeout_seconds
            timeout = loop.add_timeout(deadline, self._on_timeout) 
            self._timeout = timeout

    def _get_subscription_key(self):
        if self.resource[-2:] == '.*':
            # add to the general subscription for this resource
            return 'general:%s' % self.resource[:-2]
        else:
            # subscribing to a specific resource
            return 'specific:%s' % self.resource

    def _add_subscriber(self):
        self.subscribers[self._get_subscription_key()].add(self._on_response) 

    def _get_timeout(self):
        request_timeout = self.get_argument('timeout', None)
        if request_timeout:
            # the request specified it's own timeout
            return int(request_timeout)
        else:
            return self.application.default_timeout
    
    def _on_timeout(self):
        # always close the connection if 
        # there is a timeout
        self.set_header('Connection', 'close')
        try:
            self.write('timeout')
        except IOError:
            pass
        # clear the subscribers
        self._cleanup()
        self.finish()

    def _on_response(self, response):
        loop = tornado.ioloop.IOLoop.instance()
        try:
            loop.remove_timeout(self._timeout)
        except AttributeError:
            pass # there was no timeout set

        self.write(response)
        if self._close_connection:
            self._cleanup()
            self.finish()
        else:
            self.flush()

class PublishHandler(BaseHandler):
    def post(self, resource):
        subscribers = self._get_subscribers(resource)
        content = self.request.body

        for subscriber in subscribers:
            try:
                subscriber(content)
            except IOError:
                pass

        # clear the subscribers
        self.subscribers[resource] = set()

    def _get_subscribers(self, resource):
        subscribers = set()
        parts = resource.split('.')
        for i in xrange(len(parts)):
            part = '.'.join(parts[0:i + 1])
            s = 'general:%s' % part
            to_add = self.subscribers[s]
            subscribers.update(to_add)
        s = 'specific:%s' % resource
        to_add = self.subscribers[s]
        subscribers.update(to_add)
        return subscribers
