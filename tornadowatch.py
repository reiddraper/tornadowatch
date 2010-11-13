#!/usr/bin/env python

from collections import defaultdict

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options

import pubsub

define("port", default=8000, help="run on the given port", type=int)

class PubSub(tornado.web.Application):
    def __init__(self):
        self.subscribers    = defaultdict(set)
        self.timeouts       = defaultdict(set)
        handlers = [
        (r'/subscribe/(.+)', pubsub.SubscribeHandler),
        (r'/publish/(.+)', pubsub.PublishHandler),
        ]
        settings = {}
        tornado.web.Application.__init__(self, handlers, **settings)

def main():
    tornado.options.parse_command_line()
    application = PubSub()
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
