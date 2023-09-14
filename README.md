# xtaozi-clash

## Introduce

There are several clash/trojan nodes to be used. And sometimes, I want to share the config to others. 

However, I don't want to share all of them, so I need to generate different config for different purpose.

The script provide this two features:

* Generate config for different purpose
* Download ruleset files from remote subscribe url and upload to `Cloudflare R2`
* Upload generated config to `Cloudflare R2`


## How to use


### Config files

The repo didn't contain all config files. Some may contain sensitive information not included.

* `profiles.yaml` Define profiles to be generated. It also contains r2 config about bucket. 
* `profile_template.yaml` Template for generate profile config
* `DIR proxies` Define your proxy nodes, support local yaml files or remote subscribe url(now support boslife)
* `DIR rulesets` Local defined ruleset, support local yaml files or remote subscribe url

####  `profiles.yaml`

This config *NOT Supplied* in repo. A sample will be added later.

The config contain two parts:

* Cloudflare R2 config
* Clash profile config

### Generate

The script will generate config files for each profile defined in `profiles.yaml`.

* `proxy-groups` Filter proxy groups used by the profile
* `proxies` Filter proxies used in `proxy-groups`
* `rule-providers` Filter cannot use ruleset (for has no proxy provided)
* `rules` Filter cannot use rules (for has no ruleset or no proxy-groups provided)

```bash
python3 main.py -h
```

```text
Usage: main.py [options]

Options:
  -h, --help            show this help message and exit
  -f FILE, --file=FILE  specify profile config file
  -u, --upload          upload profile to r2
  -r, --ruleset         upload ruleset to r2 (also download ruleset from remote first)
  
```