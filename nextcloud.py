import requests
import base64
import xml.etree.ElementTree as ET
import subprocess

def get_nextcloud_file_list(username, password, nextcloud_server, remote_directory):
    """
    Args:
        username (str): nextcloud username
        password (str): nextcloud password
        nextcloud_server (str): nextcloud dav url. default: 'http://{nextcloud_server_host_port}/remote.php/dav/files/{username}'
        remote_directory (str): nextcloud specified folder

    Raises:
        Exception: can't get all file name

    Returns:
        list: specify all file names in the folder
    """
    url = f'{nextcloud_server}/{remote_directory}'
    auth = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {
        'Authorization': f'Basic {auth}',
        'Depth': '1',
        'Content-Type': 'application/xml'
    }
    propfind_body = f'''<?xml version="1.0"?>
                        <d:propfind xmlns:d="DAV:">
                            <d:prop>
                                <d:href/>
                            </d:prop>
                        </d:propfind>
                    '''
    response = requests.request('PROPFIND', url, headers=headers, data=propfind_body.encode(),
                                allow_redirects=False)

    if response.status_code == 207:
        root = ET.fromstring(response.content)
        file_elements = root.findall(".//{DAV:}href")
        file_names = [
            e.text.split('/')[-1]
            for e in file_elements
            if e is not None and e.text is not None and not e.text.endswith('/')
        ]
        return file_names
    else:
        raise Exception(f"Failed to retrieve file list with status code: {response.status_code}")
    
def upload_file_nextcloud(filename, username, password, nextcloud_server, remote_directory):
    """
    Args:
        filename (str): upload file path
        username (str): nextcloud username
        password (str): nextcloud password
        nextcloud_server (str): nextcloud dav url. default: 'http://{nextcloud_server_host_port}/remote.php/dav/files/{username}'
        remote_directory (str): nextcloud specified folder

    Raises:
        Exception: file upload failed

    Returns:
        int: process returncode
    """
    server_url = nextcloud_server + remote_directory
    command = f'curl -u {username}:{password} "{server_url}" -T "{filename}" -X PUT'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print('start_upload', process)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"File upload failed. Please check the server status with status code: {process.returncode}")
    else:
        print('File uploaded successfully!')
        return process.returncode
    
def create_folder_nextcloud(foldername, username, password, nextcloud_server, remote_directory):
    """
    Args:
        foldername (str): create folder name
        username (str): nextcloud username
        password (str): nextcloud password
        nextcloud_server (str): nextcloud dav url. default: 'http://{nextcloud_server_host_port}/remote.php/dav/files/{username}'
        remote_directory (str): nextcloud specified folder

    Raises:
        Exception: folder create failed

    Returns:
        int: process returncode
    """
    server_url = nextcloud_server + remote_directory
    command = f'curl -u {username}:{password} -X MKCOL "{server_url}"/"{foldername}"'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print('start_create', process)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"Folder create failed. Please check the server status with status code: {process.returncode}")
    else:
        print('Folder create successfully!')
        return process.returncode