def clean_s3_bucket(bucket_name, key):
    import boto3

    s3 = boto3.resource('s3')
    s3.Object(bucket_name, key).delete()
    print(f'{key} is deleted from bucket {bucket_name}')


def upload_to_s3_full(task_id, download_task_id, **kwargs):
    import os
    import boto3
    from dotenv import load_dotenv
    from airflow.models import Variable

    from helpers.constants import DUMMY_FILES_SUB_KEY

    load_dotenv()
    ti = kwargs['ti']
    full_file_path = ti.xcom_pull(key=download_task_id)

    # If s3_keys are not set in the memory yet
    try:
        Variable.get(f"{task_id}_s3_key")
    except Exception as e:
        Variable.set(f"{task_id}_s3_key", '')

    aws_access_key_id = os.getenv('ACCESS_KEY')
    aws_secret_access_key = os.getenv('SECRET_KEY')
    endpoint_url = os.getenv('ENDPOINT')
    cwd = os.getcwd()

    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        endpoint_url=endpoint_url
    )
    s3_resource = boto3.resource(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        endpoint_url=endpoint_url
    )
    download_file_name = os.path.basename(full_file_path)
    key = f'{DUMMY_FILES_SUB_KEY}/{download_file_name}'

    # uncomment if you want to celan a s3 bucket
    # for file in my_bucket.objects.all():
    #             s3_resource.Object('scoap3-test-ernesta', str(file)).delete()
    #             print(file)

    Variable.set(f"{task_id}_s3_key", key)

    s3_resource.Bucket(os.getenv('BUCKET_NAME')).put_object(
        Key=key,
        Body=open(full_file_path, 'rb')
    )
    return key
