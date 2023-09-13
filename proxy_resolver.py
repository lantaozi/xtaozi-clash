# -*- coding: utf-8 -*-

import re
import requests
import base64
import urllib.parse


class BoslifeResolver:
    def __init__(self, url) -> None:
        self.url = url

    def resolve(self):
        r = requests.get(self.url)
        proxies = []
        if r.status_code == 200:
            resp_text = base64.b64decode(r.text).decode("utf-8")
            for proxy_url in urllib.parse.unquote(resp_text).split("\r\n"):
                if len(proxy_url) > 0:
                    proxy = self._parse_trojan(proxy_url)
                    if proxy is not None:
                        proxies.append(proxy)
        return proxies

    def _parse_trojan(self, trojan_url):
        proxy_re = re.compile(r"trojan://(.*)@(.*):(.*)\?(.*)#(.*)", re.M | re.I)
        proxy_match = proxy_re.match(trojan_url)

        proxy_name = proxy_match.group(5)

        if proxy_name.startswith("[BosLife]"):
            proxy_params = {}
            for proxy_param in proxy_match.group(4).split("&"):
                proxy_param_pair = proxy_param.split("=")
                proxy_params[proxy_param_pair[0]] = proxy_param_pair[1]

            return {
                "name": proxy_name,
                "type": "trojan",
                "server": proxy_match.group(2),
                "port": int(proxy_match.group(3)),
                "password": proxy_match.group(1),
                "udp": True,
                "sni": proxy_params["sni"],
                "skip-cert-verify": proxy_params["allowInsecure"] == "1",
            }
        else:
            return None
