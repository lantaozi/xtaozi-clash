import os
import shutil

import requests
import r2


class RuleSetLoader:
    """
    Load ruleset from url and upload to r2.
    """

    def __init__(self, name, src_url, temp_dir, behavior, r2_option: r2.R2Client.Option) -> None:
        self.src_url = src_url  # may be a remote url or a local file path
        self.name = name
        self.temp_dir = temp_dir
        self.temp_path = os.path.join(temp_dir, f"{self.name}.txt")
        self.bucket_object_key = f"ruleset/{self.name}.txt"
        self.r2_option = r2_option
        self.r2_url = f"{self.r2_option.domain}{self.bucket_object_key}"
        self.behavior = behavior

    def download(self):
        if self.src_url.startswith("http"):
            self._download_remote()
        else:
            if os.path.exists(self.src_url):
                shutil.copy(self.src_url, self.temp_path)

    def _download_remote(self):
        r = requests.get(self.src_url)
        if r.status_code == 200:
            if not os.path.exists(self.temp_dir):
                os.mkdir(os.path.basename(self.temp_dir))
            with open(self.temp_path, "w") as f:
                f.write(r.text)
                f.close()
        else:
            raise Exception(f"Failed to load ruleset from {self.src_url}")

    def upload_2_r2(self) -> str:
        r2_client = r2.R2Client(self.r2_option)
        return r2_client.upload_file(self.temp_path, self.bucket_object_key)

    def generate(self):
        return {
            "type": "http",
            "behavior": self.behavior,
            "url": self.r2_url,
            "path": f"./ruleset/{self.name}.yaml",
            "interval": 86400,
        }
