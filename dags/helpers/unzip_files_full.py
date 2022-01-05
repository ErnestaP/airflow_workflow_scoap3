def unzip_files_full(task_id, file_name):
    from airflow.models import Variable

    import zipfile
    import os

    from helpers.create_dir import create_dir
    from helpers.constants import UNZIPPED_FILES_FOLDER, DOWNLOADED_FILES_FROM_S3

    cwd = os.getcwd()
    full_zipped_file_name = os.path.join(
        cwd, DOWNLOADED_FILES_FROM_S3, file_name)

    paths_for_unzipped_files = []
    grouping_folder = file_name.split(".zip")[0]
    path_for_unzipped_files = os.path.join(
        cwd, UNZIPPED_FILES_FOLDER, grouping_folder)

    with zipfile.ZipFile(full_zipped_file_name, 'r') as zip_ref:
        try:
            zip_ref.extractall(path_for_unzipped_files)
            print(f'file {path_for_unzipped_files} is extracted successfully')
            extracted_file_names = os.listdir(path_for_unzipped_files)
            for extracted_file_name in extracted_file_names:
                full_path = os.path.join(path_for_unzipped_files, extracted_file_name)
                paths_for_unzipped_files.append(full_path)
            # Need to return something, because otherwise it won't mark task as 'succeess'
        except Exception as e:
            print(
                f'Error while extracting the file {path_for_unzipped_files}: {e}')
    unzipped_files_paths_string = ",".join(paths_for_unzipped_files)
    Variable.set(f"{task_id}_unzipped_files_path", unzipped_files_paths_string)
    return unzipped_files_paths_string