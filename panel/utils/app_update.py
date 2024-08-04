import os
import sys
import requests
import zipfile
import shutil
import socket
from PySide2.QtCore import QObject, Signal, Slot
from localization import LANG_STR_ENUM, getLocalizationStr


class AppUpdate(QObject):
    update_complete = Signal()
    update_failed = Signal(str)

    def __init__(self, repo_url, download_to, extract_to, ignore_list=None):
        super().__init__()
        self.repo_url = repo_url
        self.download_to = download_to
        self.extract_to = extract_to
        self.temp_dir = os.path.join(self.download_to, 'temp_update')
        self.ignore_list = ignore_list or []
        self.retry_attempts = 3

    def download_latest_release(self):
        api_url = f'https://api.github.com/repos/{self.repo_url}/zipball/main'
        retries = 0

        while retries < self.retry_attempts:
            try:
                with requests.get(api_url, stream=True, timeout=5) as r:
                    r.raise_for_status()
                    zip_path = os.path.join(self.temp_dir, 'update.zip')
                    os.makedirs(self.temp_dir, exist_ok=True)
                    with open(zip_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)

                    with zipfile.ZipFile(zip_path, 'r') as z:
                        top_level_dir = z.namelist()[0]
                        for member in z.namelist():
                            member_path = os.path.relpath(member, start=top_level_dir)
                            if member_path != ".":
                                z.extract(member, self.temp_dir)
                                shutil.move(os.path.join(self.temp_dir, member), os.path.join(self.extract_to, member_path))

                    os.remove(zip_path)

                self.update_complete.emit()
                return

            except (requests.exceptions.RequestException, socket.timeout) as e:
                retries += 1
                if retries == self.retry_attempts:
                    self.update_failed.emit(getLocalizationStr(LANG_STR_ENUM.UI_MENU_HELP_UPDATE_ERROR_SERVER_CONNECTION) + " :: {}".format(e))
                    return

            except Exception as e:
                self.update_failed.emit(getLocalizationStr(LANG_STR_ENUM.UI_MENU_HELP_UPDATE_ERROR_DOWNLOAD_ERROR) + " :: {}".format(e))
                return

    def clean_target_directory(self):
        for root, dirs, files in os.walk(self.extract_to):
            for name in files:
                file_path = os.path.join(root, name)
                relative_path = os.path.relpath(file_path, self.extract_to)
                if not any(relative_path.startswith(ignore) for ignore in self.ignore_list):
                    os.remove(file_path)

            for name in dirs:
                dir_path = os.path.join(root, name)
                relative_path = os.path.relpath(dir_path, self.extract_to)
                if not any(relative_path.startswith(ignore) for ignore in self.ignore_list):
                    shutil.rmtree(dir_path)

    @Slot()
    def apply_update(self):
        self.clean_target_directory()
        self.download_latest_release()
        shutil.rmtree(self.temp_dir)
        sys.exit()
