# -*- coding: utf-8 -*-

# ############################################################################
# This example demonstrates how to use the MultipartEncoderMonitor to create a
# progress bar using clint.
# ############################################################################

from clint.textui.progress import Bar as ProgressBar
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

import requests


def create_callback(encoder):
    encoder_len = len(encoder)
    bar = ProgressBar(expected_size=encoder_len, filled_char='=')

    def callback(monitor):
        bar.show(monitor.bytes_read)

    return callback


def create_upload():
    return MultipartEncoder({
        'form_field': 'value',
        'another_form_field': 'another value',
        'first_file': ('progress_bar.py', open(__file__, 'rb'), 'text/plain'),
        'second_file': ('progress_bar.py', open(__file__, 'rb'),
                        'text/plain'),
        })


if __name__ == '__main__':
    encoder = create_upload()
    callback = create_callback(encoder)
    monitor = MultipartEncoderMonitor(encoder, callback)
    r = requests.post('https://httpbin.org/post', data=monitor,
                      headers={'Content-Type': monitor.content_type})
    print('\nUpload finished! (Returned status {0} {1})'.format(
        r.status_code, r.reason
        ))
