# -*- coding: utf-8 -*-
import betamax


def get_betamax(session):
    return betamax.Betamax(
        session,
        cassette_library_dir='tests/cassettes')
