import logging
import boto3
from botocore.exceptions import ClientError
import os
from time import gmtime, strftime, localtime
from datetime import datetime

# hard code
DIR_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
MONGO_DB_PATH = DIR_PATH + '/tools/database'
S3_BUCKET_DES = 'dogami-database'

LOG_DIR = DIR_PATH + '/log_move_file'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
CUR_TIME = strftime("%Y_%m_%d_%H_%M_%S", localtime())
logging.basicConfig(filename=f'{LOG_DIR}/{CUR_TIME}',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

def upload_file_to_s3(s3_client, file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        logging.info(f"Success upload file {file_name}")
    except ClientError as e:
        logging.error(e)
        return False
    return True


def upload_directory(path, bucketname):
    # Upload the file
    s3_client = boto3.client('s3')
    for root, dirs, files in os.walk(path):
        for file in files:
            today_date = datetime.today().strftime('%Y-%m-%d')
            object_name = today_date + '/' + 'database/' + file
            upload_file_to_s3(s3_client, os.path.join(root, file), bucketname, object_name)


if __name__ == '__main__':
    # print(DIR_PATH)
    logging.info("Start the program")
    upload_directory(MONGO_DB_PATH, S3_BUCKET_DES)
    logging.info("Finish the program")
