#!/usr/bin/python
import pytest

from api import app


def test_index():
  index = app.index()
  assert index == {'AWS_IR-api experimental'}
