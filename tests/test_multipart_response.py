# -*- coding: utf-8 -*-
import unittest
import mock
import requests
import six
from requests_toolbelt.multipart import MultipartDecoder
from requests_toolbelt.multipart import MultipartEncoder
from requests_toolbelt.multipart import Subpart
from requests_toolbelt.multipart import NonMultipartContentTypeException


class TestSubpart(unittest.TestCase):
    @classmethod
    def make_part_bytes(cls, header, value, encoding):
        return b'\r\n\r\n'.join(
            [
                b'\r\n'.join(
                    [
                        b': '.join([i.encode(encoding) for i in h])
                        for h in header
                    ]
                ),
                value.encode(encoding)
            ]
        )

    def setUp(self):
        self.header_1 = (six.u('Snowman'), six.u('☃'))
        self.value_1 = six.u('©')
        self.part1 = Subpart(TestSubpart.make_part_bytes((self.header_1,), self.value_1, 'utf-8'), 'utf-8')
        self.part2 = Subpart(TestSubpart.make_part_bytes((self.header_1,), self.value_1, 'utf-8'), 'utf-8')
        self.part3 = Subpart(TestSubpart.make_part_bytes((self.header_1,), self.value_1, 'utf-16'), 'utf-16')

    def test_equality_content_should_be_equal(self):
        self.assertEqual(self.part1, self.part2)

    def test_equality_content_should_not_equal(self):
        self.assertNotEqual(self.part1, self.part3)

    def test_equality_content_should_equal_bytes(self):
        self.assertEqual(self.part1.content, self.value_1.encode('utf-8'))

    def test_equality_content_should_not_equal_bytes(self):
        self.assertNotEqual(self.part1.content, self.value_1.encode('utf-16'))

    def test_changing_encoding_changes_text(self):
        part3_orig = self.part3.text
        self.part3.encoding = 'latin-1'
        self.assertNotEqual(self.part3.text, part3_orig)

    def test_text_should_be_equal(self):
        self.assertEqual(self.part3.text, self.value_1)


class TestMultipartDecoder(unittest.TestCase):
    def _make_mock_response(self, encoder_instance):
        response = mock.NonCallableMagicMock(spec=requests.Response)
        response.content = encoder_instance.to_string()
        response.encoding = encoder_instance.encoding
        response.headers = {'content-type': encoder_instance.content_type}
        return response

    def setUp(self):
        self.parts = (
            (
                ('field', 'value'),
                ('other field', 'other value'),
                ('third field', 'third value'),
                ('fourth field', 'fourth value'),
                ('fifth field', 'fifth value'),
                ('sixth field', 'sixth value')
            ),
            (
                ('additional field', 'additional value'),
                ('extra field', 'extra value')
            ),
            (('another field', 'another value'), ('more field', 'more value'))
        )
        self.boundary = 'sample boundary'
        self.encoder_instances = [
            MultipartEncoder(ps, self.boundary) for ps in self.parts
        ]
        self.response_instances = [
            self._make_mock_response(enc_ins)
            for enc_ins in self.encoder_instances
        ]
        self.decoder_instances = [
            MultipartDecoder(resp) for resp in self.response_instances
        ]

    def test_non_multipart_response_fails(self):
        jpeg_response = mock.NonCallableMagicMock(spec=requests.Response)
        jpeg_response.headers = {'content-type': 'image/jpeg'}
        self.assertRaises(
            NonMultipartContentTypeException, MultipartDecoder, jpeg_response
        )

    def test_decoded_data_same_as_what_was_encoded(self):
        self.assertListEqual(
            [
                orig_part[1]
                for orig_parts in self.parts
                for orig_part in orig_parts
            ],
            [
                dc_part.text
                for decoder in self.decoder_instances
                for dc_part in decoder
            ]
        )

    def test_number_of_parts_is_correct(self):
        self.assertListEqual(
            [len(part) for part in self.parts],
            [len(decoder) for decoder in self.decoder_instances]
        )

    def test_proxies_unknown_attributes_to_response_component(self):
        self.assertListEqual(
            [resp.encoding for resp in self.response_instances],
            [decoder.encoding for decoder in self.decoder_instances]
        )

    def test_attributes_unknown_by_both_throws_appropriate_error(self):
        self.assertRaises(AttributeError, getattr, self.decoder_instances[0], 'blah')

    def test_subpart_headers_are_correct(self):
        self.assertListEqual(
            [
                b''.join(
                    (
                        b'form-data; name="',
                        orig_part[0].encode('utf-8'),
                        b'"'
                    )
                )
                for orig_parts in self.parts
                for orig_part in orig_parts
            ],
            [
                dc_part.headers[b'Content-Disposition']
                for decoder in self.decoder_instances
                for dc_part in decoder
            ]
        )

    def test_concatenate_decoders(self):
        self.assertListEqual(
            [
                orig_part[1]
                for orig_parts in self.parts
                for orig_part in orig_parts
            ],
            [
                part.text
                for part in (
                    self.decoder_instances[0] +
                    self.decoder_instances[1] +
                    self.decoder_instances[2]
                )
            ]
        )

    def test_in_place_decoder_concatenation(self):
        self.decoder_instances[0] += self.decoder_instances[1]
        self.decoder_instances[0] += self.decoder_instances[2]
        self.assertListEqual(
            [
                orig_part[1]
                for orig_parts in self.parts
                for orig_part in orig_parts
            ],
            [part.text for part in self.decoder_instances[0]]
        )

    def test_n_copies_concatenated(self):
        self.assertListEqual(
            [
                orig_part[1]
                for orig_part in self.parts[0]*3
            ],
            [part.text for part in self.decoder_instances[0]*3]
        )

    def test_n_copies_concatenated_in_place(self):
        self.decoder_instances[0] *= 3
        self.assertListEqual(
            [
                orig_part[1]
                for orig_part in self.parts[0]*3
            ],
            [part.text for part in self.decoder_instances[0]]
        )

    def test_slicing_no_stop(self):
        self.assertListEqual(
            [
                orig_part[1]
                for orig_parts in self.parts
                for orig_part in orig_parts[1:]
            ],
            [
                part.text
                for decoder in self.decoder_instances
                for part in decoder[1:]
            ]
        )

    def test_indexing(self):
        self.assertListEqual(
            [orig_parts[1][1] for orig_parts in self.parts],
            [decoder[1].text for decoder in self.decoder_instances]
        )

    def test_negative_indexing(self):
        self.assertListEqual(
            [orig_parts[-1][1] for orig_parts in self.parts],
            [decoder[-1].text for decoder in self.decoder_instances]
        )

    def test_slicing_no_start(self):
        self.assertListEqual(
            [
                orig_part[1]
                for orig_parts in self.parts
                for orig_part in orig_parts[:-1]
            ],
            [
                part.text
                for decoder in self.decoder_instances
                for part in decoder[:-1]
            ]
        )

    def test_slicing_only_step(self):
        self.assertListEqual(
            [
                orig_part[1]
                for orig_parts in self.parts
                for orig_part in orig_parts[::2]
            ],
            [
                part.text
                for decoder in self.decoder_instances
                for part in decoder[::2]
            ]
        )

    def test_slicing_start_stop_step(self):
        self.assertListEqual(
            [
                orig_part[1]
                for orig_parts in self.parts
                for orig_part in orig_parts[1:-2:2]
            ],
            [
                part.text
                for decoder in self.decoder_instances
                for part in decoder[1:-2:2]
            ]
        )
