import os.path
import shutil

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
        print(f"Uploading ruleset [{ruleset_name}] to r2...")
        r2_client.upload_file(ruleset_loader.temp_path, ruleset_loader.bucket_object_key)


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
        print("========================================")
        print(f"Rendering profile {profile.name}...")
        print("----------------------------------------")
        profile.render(all_proxy_groups, all_ruleset, all_rules)
        profile.export(export_to)
        print(f"Profile {profile.name} rendered to {export_to}.")
        if upload_to_r2:
            r2_client.upload_file(export_to, f"profile/{profile.name}.yaml")


if __name__ == "__main__":
    _config_file_path = "config/profiles.yaml"
    _temp_dir = "./temp"
    _output_dir = "./output"

    if os.path.exists(_temp_dir):
        shutil.rmtree(_temp_dir)
    os.mkdir(_temp_dir)

    if os.path.exists(_output_dir):
        shutil.rmtree(_output_dir)
    os.mkdir(_output_dir)

    upload_ruleset(_config_file_path, _temp_dir)
    # generate_profiles(_config_file_path, _temp_dir, _output_dir, False)

    shutil.rmtree(_temp_dir)
