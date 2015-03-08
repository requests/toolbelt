try:
    import Queue as queue
except:
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

p = pool.Pool(q)
