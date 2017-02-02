""" Uploads a stream to S3 """

class S3Uploader(object):
    def __init__(self, bucket, client):
        """
            Takes an s3 bucket identifier
            and an s3 client
        """
        self.client = client
        self.bucket = bucket

    def upload(self, file):
        pass

    def validate(self, file):
        """
            Runs list bucket checks for the presence of file
            and that file is appropriately sized
        """
        pass

    def __check_file_size(self, bucket_list, file):
        """
            Compares two file sizes remote and local
            returns bool on success
        """
        pass

    def __check_file_present(self, bucket_list, file_name):
        """
            Validates file is present in client bucket
        """
        pass
