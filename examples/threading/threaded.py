try:
    import Queue as queue
except ImportError:
    import queue

from requests_toolbelt.threaded import pool

q = queue.Queue()
q.put({
    'method': 'GET',
    'url': 'https://httpbin.org/get',
    'params': {'foo': 'bar'}
})
q.put({
    'method': 'POST',
    'url': 'https://httpbin.org/post',
    'json': {'foo': 'bar'}
})
q.put({
    'method': 'POST',
    'url': 'https://httpbin.org/post',
    'data': {'foo': 'bar'}
})
q.put({
    'method': 'PUT',
    'url': 'https://httpbin.org/put',
    'files': {'foo': ('', 'bar')}
})
q.put({
    'method': 'GET',
    'url': 'https://httpbin.org/stream/100',
    'stream': True
})
q.put({
    'method': 'GET',
    'url': 'https://httpbin.org/delay/10',
    'timeout': 5.0
})

for i in range(30):
    q.put({
        'method': 'GET',
        'url': 'https://httpbin.org/get',
        'params': {'i': str(i)},
    })

p = pool.Pool(q)
p.join_all()

responses = list(p.responses())
exceptions = list(p.exceptions())
