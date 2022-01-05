UNZIPPED_FILES_FOLDER = "unzipped"
DOWNLOADED_FILES_FOLDER = "downloaded"
DUMMY_FILES_SUB_KEY = "dummy_files"
DOWNLOADED_FILES_FROM_S3="downloaded_from_s3"
PARSED_JSONS = "jsons"

dags_names = {
    'download_files': 'download_files',
    'unzip_files': 'unzip_dag',
    'parse': 'parse_dag',
    'full_pipeline': 'full_pipeline'
}
