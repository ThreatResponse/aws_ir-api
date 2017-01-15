#!/usr/bin/python

import pytest
import boto3
import base64
import os
import json
import time
import uuid

from faker import Factory
from dotenv import Dotenv
from api import app as awsirapi

def test_index():
    result = awsirapi.index()
    assert result == {'AWS_IR-api': 'experimental'}
