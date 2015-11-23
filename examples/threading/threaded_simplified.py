from requests_toolbelt import threaded

requests = [{
    'method': 'GET',
    'url': 'https://httpbin.org/get',
    'params': {'foo': 'bar'}
}, {
    'method': 'POST',
    'url': 'https://httpbin.org/post',
    'json': {'foo': 'bar'}
}, {
    'method': 'POST',
    'url': 'https://httpbin.org/post',
    'data': {'foo': 'bar'}
}, {
    'method': 'PUT',
    'url': 'https://httpbin.org/put',
    'files': {'foo': ('', 'bar')}
}, {
    'method': 'GET',
    'url': 'https://httpbin.org/stream/100',
    'stream': True
}, {
    'method': 'GET',
    'url': 'https://httpbin.org/delay/10',
    'timeout': 2.0
}]

url = 'https://httpbin.org/get'
requests.extend([
    {'method': 'GET', 'url': url, 'params': {'i': str(i)}}
    for i in range(30)
])

responses, exceptions = threaded.map(requests)
