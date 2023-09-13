import glob

import yaml

import clash_profile
import proxy_resolver
import r2
import ruleset_resolver


class ConfigParser:
    def __init__(self, path) -> None:
        self.path = path
        with open(path, 'r') as config_file:
            self.config = yaml.safe_load(config_file)
            config_file.close()
        if self.config is None:
            raise EOFError("No config used, check file profiles.yaml")

    def parse_r2_option(self):
        r2_option = self.config["r2"]
        return r2.R2Client.Option(
            account_id=r2_option["account_id"],
            access_key_id=r2_option["access_key_id"],
            access_key_secret=r2_option["access_key_secret"],
            domain=r2_option["domain"],
            bucket=r2_option["bucket"]
        )

    def parse_profiles(self):
        profile_map = {}
        for conf in self.config["clash"]["profile"]:
            profile_name = conf["name"]
            proxy_groups = []
            for proxy_group_conf in conf["proxy"]:
                pg_name = proxy_group_conf["name"]
                pg_use = proxy_group_conf["use"] if "use" in proxy_group_conf else None
                proxy_groups.append(clash_profile.ProxyGroup(name=pg_name, target=pg_use))
            profile = clash_profile.ClashProfile(
                name=profile_name,
                template_path=conf["template"],
                proxy_groups=proxy_groups
            )
            profile_map[profile_name] = profile
        return profile_map

    def parse_proxies(self):
        proxies = {}
        for url in self.config["clash"]["proxy"]:
            if url.startswith('http'):  # remote url
                _proxies = proxy_resolver.BoslifeResolver(url).resolve()
                for proxy in _proxies:
                    if proxy['name'] not in proxies:
                        proxies[proxy['name']] = proxy
            else:  # local file
                for path in glob.glob(url):
                    with open(path, 'r') as f:
                        for proxy in yaml.safe_load(f)["proxies"]:
                            if proxy['name'] not in proxies:
                                proxies[proxy['name']] = proxy
                        f.close()
        return proxies

    def parse_proxy_proups(self, all_proxies):
        # 解析所有proxy，格式map：<name to proxies>
        proxy_groups = {}
        for conf in self.config["clash"]["proxy-group"]:
            pg_name = conf["name"]
            pg_proxies = conf["proxies"]
            for proxy in pg_proxies:
                if proxy in all_proxies:
                    if pg_name not in proxy_groups:
                        proxy_groups[pg_name] = []
                    proxy_groups[pg_name].append(all_proxies[proxy])
                else:
                    print(f"!!! Proxy {proxy} not found")
        return proxy_groups

    def parse_ruleset(self, temp_dir, r2_option):
        # 解析所有ruleset，格式map：<name to path>
        ruleset = {}
        for conf in self.config["clash"]["rule-provider"]:
            rp_url = conf["url"]
            loader = ruleset_resolver.RuleSetLoader(rp_url, temp_dir, r2_option)
            ruleset[loader.name] = loader
        return ruleset
