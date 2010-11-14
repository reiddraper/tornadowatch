# tornadowatch

`tornadowatch` is a simple HTTP publish/subscribe server written in [tornado](http://www.tornadoweb.org/ "tornado"). It has been tested with python 2.5 and 2.6, and [tornado v1.1.0](https://github.com/facebook/tornado/tree/v1.1.0 "v1.1.0").

## features

* handles many concurrent connections
* wildcard topic names. eg. sports.soccer.* (the .* can only occur at the end of the topic name)
* optional subscription connection closing after one publication
* optional timeouts

## persistent connection example

Open up three terminal windows and type:

1. `python tornadowatch.py`
2. `curl -X GET --no-buffer "localhost:8000/subscribe/test"`
3. `curl -X POST "localhost:8000/publish/test" -d "Hello, World"`

In terminal 2 you will see the server has responded with "Hello, World". Notice the connection on terminal 2 remains open, ready to receive additional publications to the *test* topic.

## notification example

You can subscribe to a topic, and have the connection closed as soon as you receive one message. This is useful for situations where there will only ever be one publication for a topic. For example, you could use the server for a queue worker to signal that it was completed a unique task identifier. Replace the terminal 2 request above with:

`curl -X GET -H "Connection: close" "localhost:8000/subscribe/test"`

## wildcard topic subscription

You can subscribe to topics as general or specifically as you like. Here are some examples.

1. `/subscribe/sports.soccer` will only receive publications to `sports.soccer` exactly.
2. `/subscribe/sports.*` will receive publications to `sports`, `sports.soccer`, `sports.basketball`, etc.
3. `/subscribe/.*` will receive publications sent to any topic

## timeout example

You can ask the server to close the connection after a specified number of seconds. For example:

`curl -X GET "localhost:8000/subscribe/test?timeout=60`

## TODO

* add support for websockets

