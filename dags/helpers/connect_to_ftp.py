
def connect_to_ftp():
    import ftputil
    from  helpers.ftp_connection import ftp_session_factory
    import os 

    ftp_host = ftputil.FTPHost(os.getenv('FTP_HOST'),
                               os.getenv('FTP_USER'),
                               os.getenv('FTP_PASSWORD'),
                               session_factory=ftp_session_factory)

    ftp_host.use_list_a_option = False
    ftp_host.chdir('dummy_test_dir')
    path = ftp_host.getcwd()
    
    # Upload files to ftp if they not there
    # if 'dummy_test_dir' in path:
    #     ftp_host.upload_if_newer('oup.xml.zip', 'oup.xml.zip')
    #     ftp_host.upload_if_newer('scoap3.archival.zip', 'scoap3.archival.zip')
    #     ftp_host.upload_if_newer('scoap3.pdf.zip', 'scoap3.pdf.zip')
    return ftp_host
