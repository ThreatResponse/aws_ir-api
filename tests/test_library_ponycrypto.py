#!/usr/bin/python

import pytest
import boto3
import hashlib

from api.chalicelib import ponycrypto

CLIENT = boto3.client('kms')

TEST_STRING = "IncidentPonySavedTheDay"

def get_kms_key():
    """
        Function uses pre-generated fixture key
        Ensure that this key exists in the account
    """

    arn = "arn:aws:kms:us-west-2:576309420438:key/1fe91e7c-52bb-4ada-8447-11484eb78ddb"
    return arn

def setup_test():
    pass

def test_object_initialize():
    arn = get_kms_key()
    p = ponycrypto.PonyCrypto(arn, CLIENT)
    assert p is not None

def test_encrypt():
    arn = get_kms_key()
    p = ponycrypto.PonyCrypto(arn, CLIENT)
    ciphertext = p.encrypt(TEST_STRING)
    assert ciphertext is not None

def test_hash():
    arn = get_kms_key()
    p = ponycrypto.PonyCrypto(arn, CLIENT)
    pony_hash = p.hash_payload(TEST_STRING)
    h = hashlib.new('sha256')
    h.update(TEST_STRING)
    this_hash = h.hexdigest()
    assert this_hash == pony_hash

def teardown_test():
    pass
