import pytest
import boto3
import hashlib
import uuid

from api.chalicelib import uploader

CLIENT = boto3.client('s3')
UUID = uuid.uuid4().hex

def setup_test():
    response = CLIENT.create_bucket(
        Bucket=UUID,
        CreateBucketConfiguration={
            'LocationConstraint': 'us-west-2'
        }
    )
    pass

def test_initialize():
    u = uploader.S3Uploader(
        UUID,
        CLIENT
    )

    assert u is not None

def test_upload():
    u = uploader.S3Uploader(
        UUID,
        CLIENT
    )

    result = u.upload('Thisisasampleofsomecontent', 'TestFileName')
    assert result is not None


def test_validate():
    u = uploader.S3Uploader(
        UUID,
        CLIENT
    )

    result = u.validate('Thisisasampleofsomecontent', 'TestFileName')
    assert result is True


def teardown_test():
    try:
        CLIENT.delete_objects(
            Bucket=UUID,
            Delete={
                'Objects': [
                    {
                        'Key': 'TestFileName'
                    }
                ]
            }
        )

        response = CLIENT.delete_bucket(
            Bucket=UUID
        )
    except:
        pass
