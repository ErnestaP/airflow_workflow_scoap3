def create_dir(dir_path, *dir_name):
    import os
    
    full_dir_path = os.path.join(dir_path, *dir_name)
    try:
        if os.path.exists(full_dir_path):
            print(f'{dir_name} folder already exists')
            return True
        else:
            os.mkdir(full_dir_path)
            return True
    except:
        return False
