#!/bin/sh

if python tests/am_i_on_2.6.py; then pip install -U unittest2; fi