# xtaozi-clash

## Introduce

This script totally used to generate clash configs for different purpose. Some for self-use or some for sharing.

And upload ruleset and profiles to `Cloudflare R2`.

The script only generate these config part:

* `proxy-groups` Defined in `profiles.yaml`
* `proxies` Only generate proxies that used in `proxy-groups`
* `rule-providers` Filter cannot use ruleset (for has no proxy provided)
* `rules` Filter cannot use rules (for has no ruleset or no proxy-groups provided)

## How to use


### Config files

The repo didn't contain all config files. Some may contain sensitive information not included.

* `profiles.yaml` Define profiles to be generated. It also contains r2 config about bucket. This config *NOT Supplied* in repo. A sample will be added later.
* `DIR proxies` Define your proxy nodes, support local yaml files or remote subscribe url(now support boslife)
* `DIR rulesets` Local defined ruleset, support local yaml files or remote subscribe url
* `profile_template.yaml` Template for generate profile config

### Generate

There are two steps provided to generate config:

* Download ruleset files and upload to `Cloudflare R2`
* Generate config files

Both features can be used separately. Check the source in `main.py` for more details.

```bash
python3 main.py
```