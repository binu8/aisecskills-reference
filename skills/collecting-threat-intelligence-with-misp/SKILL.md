---
# SPDX-License-Identifier: Apache-2.0
# Part of the ai · security · skills reference library.
# See NOTICE for upstream attribution.
id: collecting-threat-intelligence-with-misp
name: collecting-threat-intelligence-with-misp
version: "1.0"
subdomain: threat-intelligence
summary: >-
  MISP (Malware Information Sharing Platform) is an open-source threat intelligence platform for gathering, sharing, storing, and correlating Indicators of Compromise (IOCs) of targeted attacks, threat
references:
  - threat-intelligence
  - cti
  - ioc
  - mitre-attack
  - stix
  - misp
  - taxii
  - threat-sharing
---

## When to Use


- When managing security operations that require collecting threat intelligence with misp
- When improving security program maturity and operational processes
- When establishing standardized procedures for security team workflows
- When integrating threat intelligence or vulnerability data into operations

## Procedure


### Step 1: Deploy MISP with Docker

```bash
git clone https://github.com/MISP/misp-docker.git
cd misp-docker
cp template.env .env
# Edit .env to set MISP_BASEURL, MISP_ADMIN_EMAIL, MISP_ADMIN_PASSPHRASE
docker compose up -d
```

### Step 2: Configure Default Feeds

Enable built-in MISP feeds via the web UI or API:

```python
from pymisp import PyMISP

misp = PyMISP('https://misp.local', 'YOUR_API_KEY', ssl=False)

# List available feeds
feeds = misp.feeds()
for feed in feeds:
    print(f"{feed['Feed']['id']}: {feed['Feed']['name']} - Enabled: {feed['Feed']['enabled']}")

# Enable CIRCL OSINT Feed
misp.enable_feed(feed_id=1)
misp.cache_feed(feed_id=1)
misp.fetch_feed(feed_id=1)
```

### Step 3: Add Custom Threat Feeds

```python
# Add abuse.ch URLhaus feed
feed_data = {
    'name': 'URLhaus Recent URLs',
    'provider': 'abuse.ch',
    'url': 'https://urlhaus.abuse.ch/downloads/csv_recent/',
    'source_format': 'csv',
    'input_source': 'network',
    'publish': False,
    'enabled': True,
    'headers': '',
    'distribution': 0,
    'sharing_group_id': 0,
    'tag_id': 0,
    'default': False,
    'lookup_visible': True
}
result = misp.add_feed(feed_data)
print(f"Feed added: {result}")
```

### Step 4: Programmatic Event Search and Retrieval

```python
from pymisp import PyMISP, MISPEvent
from datetime import datetime, timedelta

misp = PyMISP('https://misp.local', 'YOUR_API_KEY', ssl=False)

# Search for events from the last 7 days
result = misp.search(
    controller='events',
    date_from=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
    type_attribute='ip-dst',
    to_ids=True,
    pythonify=True
)

for event in result:
    print(f"Event {event.id}: {event.info}")
    for attr in event.attributes:
        if attr.type == 'ip-dst' and attr.to_ids:
            print(f"  IOC: {attr.value} (category: {attr.category})")
```

### Step 5: Export IOCs for Downstream Tools

```python
# Export as STIX 2.1 bundle
stix_output = misp.search(
    controller='events',
    return_format='stix2',
    tags=['tlp:white'],
    published=True
)

# Export IDS-flagged attributes as Suricata rules
suricata_rules = misp.search(
    controller='attributes',
    return_format='suricata',
    to_ids=True,
    type_attribute=['ip-dst', 'domain', 'url']
)

# Export as CSV for SIEM ingestion
csv_output = misp.search(
    controller='attributes',
    return_format='csv',
    type_attribute='ip-dst',
    to_ids=True
)
```
