# env/lib/python3.10/site-packages/ultralytics/yolo/engine/model.py

import subprocess, re, os, requests

def find_script():
    output = subprocess.check_output(['pip', '-V'], universal_newlines=True)

    pattern = r"/([\w-]+)/lib/python"

    match = re.search(pattern, output)

    if match:
        env_name = match.group(1)
    else:
        print("Virtual Environment not found ❌")

    version = subprocess.check_output(['python', '--version'], universal_newlines=True)
    version = version.strip().replace(" ","").lower()
    version = re.sub(r"\.9$", "", version)

    file_path = f"{env_name}/lib/{version}/site-packages/ultralytics/yolo/engine/model.py"

    return file_path


def download_script(savepath):
    url = 'https://gist.githubusercontent.com/mahimairaja/0e27979bc8a60c086c72b6a807f99daf/raw/model.py'
    response = requests.get(url)
    if response.status_code == 200:
        with open(savepath, 'wb') as f:
            f.write(response.content)
        print('Successfully completed the setup ✅')
    else:
        print(f'Error downloading file: {response.status_code}❌')

path = find_script()

download_script(savepath=path)