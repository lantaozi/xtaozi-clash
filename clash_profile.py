import os
import yaml


class ArrayIndentDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


class ClashProfile:
    def __init__(self, name, template_path, proxy_groups) -> None:
        self.name = name
        self.proxy_groups = proxy_groups
        with open(template_path, "r") as f:
            self.template = yaml.safe_load(f)
            f.close()

    def render(self, all_proxy_groups: dict, all_ruleset: dict, all_rules: list):
        use_proxies = {}
        use_proxy_groups = {}
        use_rules = []
        use_ruleset = {}
        for proxy_group in self.proxy_groups:
            if proxy_group.target in all_proxy_groups:
                group_proxies: list = all_proxy_groups[proxy_group.target]
                use_proxy_groups[proxy_group.name] = list(map(lambda _p: _p["name"], group_proxies))
                for proxy in group_proxies:
                    use_proxies[proxy["name"]] = proxy
        for rule in all_rules:
            (rule_type, rule_target, rule_proxy, no_resolve) = self.analyze_rule(rule)
            if rule_proxy == "DIRECT" or rule_proxy == "REJECT" or rule_proxy in use_proxy_groups:
                if rule_type == "RULE-SET":
                    if rule_target in all_ruleset:
                        use_rules.append(rule)
                        use_ruleset[rule_target] = all_ruleset[rule_target].generate()
                    else:
                        print(f"!!! RuleSet {rule_target} not found")
                else:
                    use_rules.append(rule)

        # render proxies
        self.template.pop("proxies")
        self.template["proxies"] = list(use_proxies.values())

        # render proxy-groups
        self.template.pop("proxy-groups")
        self.template["proxy-groups"] = list(map(lambda name: {
            "name": name,
            'type': 'select',
            'proxies': use_proxy_groups[name]
        }, use_proxy_groups))

        # render rule-providers
        self.template.pop("rule-providers")
        self.template["rule-providers"] = use_ruleset

        # render rules
        self.template.pop("rules")
        self.template["rules"] = use_rules

    def export(self, output_file_name):
        output_dir = os.path.dirname(output_file_name)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_file_name, "w", encoding="utf-8") as f:
            yaml.dump(
                self.template,
                stream=f,
                Dumper=ArrayIndentDumper,
                sort_keys=False,
                allow_unicode=True,
            )

    def analyze_rule(self, rule: str) -> tuple:
        rule_expr_list = rule.split(",")
        rule_type = rule_expr_list[0]
        if rule_type == "MATCH":
            return rule_type, "", rule_expr_list[1], ""
        else:
            rule_target = rule_expr_list[1]
            return rule_type, rule_target, rule_expr_list[2], rule_expr_list[3] if len(rule_expr_list) > 3 else ""


class ProxyGroup:
    def __init__(self, name, target=None):
        self.name = name
        self.target = (target, name)[target is None]
