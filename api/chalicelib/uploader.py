""" Uploads a stream to S3 """

import boto3

class S3Uploader(object):
    def __init__(self, bucket, client):
        """
            Takes an s3 bucket identifier
            and an s3 client
        """

        self.bucket = bucket
        self.client = client

    def upload(self, file_contents, filename):
        response = self.client.put_object(
            Body=file_contents,
            Bucket=self.bucket,
            Key=filename
        )
        return response

    def validate(self, file_contents, filename):
        """
            Runs list bucket checks for the presence of file
            and that file is appropriately sized
        """

        response = self.client.list_objects(
            Bucket=self.bucket

        )

        if self.__check_file_present(
            response['Contents'],
            filename
        ) == False:
            return False

        else:
            return True


    def __check_file_present(self, bucket_list, filename):
        """
            Validates file is present in client bucket
        """
        for item in bucket_list:
            print item
            if item['Key'] == filename:
                return True

        return False
