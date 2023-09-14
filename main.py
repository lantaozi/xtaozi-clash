import os.path
import shutil
from optparse import OptionParser

import config_parser
import r2


def upload_ruleset(config_file_path, temp_dir):
    print(f"Parsing config from {_config_file_path}...")
    parser = config_parser.ConfigParser(config_file_path)
    r2_option = parser.parse_r2_option()
    all_ruleset = parser.parse_ruleset(temp_dir, r2_option)
    r2_client = r2.R2Client(r2_option)

    for ruleset_name in all_ruleset:
        ruleset_loader = all_ruleset[ruleset_name]
        ruleset_loader.download()
        r2_client.upload_file(ruleset_loader.temp_path, ruleset_loader.bucket_object_key)
        print(f"Ruleset [{ruleset_name}] uploaded to r2")


def generate_profiles(config_file_path, temp_dir, output_dir, upload_to_r2=False):
    print(f"Parsing config from {_config_file_path}...")
    parser = config_parser.ConfigParser(config_file_path)

    r2_option = parser.parse_r2_option()

    print(f" parsing profiles...")
    profiles = parser.parse_profiles()
    print(f" parsing proxies...")
    all_proxies = parser.parse_proxies()
    print(f" parsing proxy groups...")
    all_proxy_groups = parser.parse_proxy_groups(all_proxies)
    print(f" parsing ruleset...")
    all_ruleset = parser.parse_ruleset(temp_dir, r2_option)
    print(f" parsing rules...")
    all_rules = parser.parse_rules()

    r2_client = r2.R2Client(r2_option)

    for profile_name in profiles:
        profile = profiles[profile_name]
        export_to = os.path.join(output_dir, f"{profile.name}.yaml")
        print("=================================================================")
        print(f"Rendering profile {profile.name}")
        print("---------------------------------")
        profile.render(all_proxy_groups, all_ruleset, all_rules)
        profile.export(export_to)
        print(f"Profile {profile.name} rendered to {export_to}.")
        if upload_to_r2:
            r2_client.upload_file(export_to, f"profile/{profile.name}.yaml")
            print(f"Profile {profile.name} uploaded to r2.")


if __name__ == "__main__":

    option_parser = OptionParser()
    option_parser.add_option("-f", "--file", dest="config_file", default="./config/profiles.yaml",
                             help="specify profile config file", metavar="FILE")
    option_parser.add_option("-u", "--upload", dest="upload_profile_to_r2", action="store_true", default=False,
                             help="upload profile to r2")
    option_parser.add_option("-r", "--ruleset", dest="upload_ruleset_to_r2", action="store_true", default=False,
                             help="upload ruleset to r2")
    (options, args) = option_parser.parse_args()
    _config_file_path = options.config_file
    _upload_profile_2_r2 = options.upload_profile_to_r2
    _upload_ruleset_2_r2 = options.upload_ruleset_to_r2

    _temp_dir = "./temp"
    _output_dir = "./output"

    if os.path.exists(_temp_dir):
        shutil.rmtree(_temp_dir)
    os.mkdir(_temp_dir)

    if os.path.exists(_output_dir):
        shutil.rmtree(_output_dir)
    os.mkdir(_output_dir)

    if _upload_ruleset_2_r2:
        upload_ruleset(_config_file_path, _temp_dir)

    generate_profiles(_config_file_path, _temp_dir, _output_dir, _upload_profile_2_r2)

    shutil.rmtree(_temp_dir)
