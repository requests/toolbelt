"""Test module for requests_toolbelt.utils.formdata."""
try:
    from urllib.parse import parse_qs
except ImportError:
    from urlparse import parse_qs

from requests_toolbelt.utils.formdata import urlencode

dict_query = {
    'first_nested': {
        'second_nested': {
            'third_nested': {
                'fourth0': 'fourth_value0',
                'fourth1': 'fourth_value1',
            },
            'third0': 'third_value0',
        },
        'second0': 'second_value0',
    },
    'outter': 'outter_value',
}

list_query = [
    ('first_nested', [
        ('second_nested', [
            ('third_nested', [
                ('fourth0', 'fourth_value0'),
                ('fourth1', 'fourth_value1'),
            ]),
            ('third0', 'third_value0'),
        ]),
        ('second0', 'second_value0'),
    ]),
    ('outter', 'outter_value'),
]

expected_parsed_query = {
    'first_nested[second0]': ['second_value0'],
    'first_nested[second_nested][third0]': ['third_value0'],
    'first_nested[second_nested][third_nested][fourth0]': ['fourth_value0'],
    'first_nested[second_nested][third_nested][fourth1]': ['fourth_value1'],
    'outter': ['outter_value'],
}


def test_urlencode_flattens_nested_dict_structures():
    """Show that when parsed, the dict structure is conveniently flat."""
    parsed = parse_qs(urlencode(dict_query))

    assert parsed == expected_parsed_query


def test_urlencode_flattens_nested_list_structures():
    """Show that when parsed, the list structure is conveniently flat."""
    parsed = parse_qs(urlencode(list_query))

    assert parsed == expected_parsed_query
