# tornadowatch

`tornadowatch` is a simple HTTP publish/subscribe server written in [tornado](http://www.tornadoweb.org/ "tornado"), it has been tested with python 2.5 and 2.6, with [tornado v1.1.0](https://github.com/facebook/tornado/tree/v1.1.0 "v1.1.0").

## example

Open up three terminal windows and type:

1. `python tornadowatch.py`
2. `curl -X GET "localhost:8000/subscribe/test"`
3. `curl -X POST "localhost:8000/publish/test" -d "Hello, World"`

In terminal 2 you will see the server has responded with "Hello, World". The connection in terminal 2 has also closed, this is because the original use of the server was for one-time notification of events completing.
