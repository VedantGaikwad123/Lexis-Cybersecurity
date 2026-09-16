# MailXray — Advanced Email Threat Investigation & SOC Analysis Platform

## Project Overview

**MailXray** is a SOC-oriented Email Threat Investigation and Threat Intelligence Platform that analyzes suspicious emails, extracts and verifies Indicators of Compromise (IOCs), correlates evidence, determines risk, and produces analyst-ready investigation reports.

The platform goes beyond a simple phishing detector by combining:

- Email forensics and header analysis
- Sender, Reply-To, and Return-Path analysis
- SPF / DKIM / DMARC inspection
- URL and attachment analysis
- Social-engineering detection
- IOC extraction
- Threat-intelligence verification
- Evidence correlation
- Automated risk scoring
- Analyst verdicts
- Campaign correlation
- Attack-chain reconstruction
- Professional SOC reporting

---

# 1. New Advanced Feature — ThreatGraph

## Email Attack Graph & Campaign Attribution Engine

**ThreatGraph** is the major advanced feature added to MailXray.

It transforms isolated indicators into an interactive relationship graph connecting:

- Emails
- Sender addresses
- Domains
- URLs
- IP addresses
- Attachments
- File hashes
- Message-IDs
- Mail servers
- ASNs
- Threat-intelligence findings
- Campaigns

Instead of investigating every IOC independently, analysts can visualize the potential infrastructure and relationships behind a phishing campaign.

```text
                         SUSPICIOUS EMAIL
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
           SENDER              URL           ATTACHMENT
              │                 │                 │
              ▼                 ▼                 ▼
           DOMAIN              IP              SHA-256
              │                 │
              └────────────┬────┘
                           ▼
                    CAMPAIGN CLUSTER
                           │
                 ┌─────────┼─────────┐
                 ▼         ▼         ▼
              Email 1    Email 2    Email 3
```

---

# 2. Why ThreatGraph Matters

A traditional investigation might identify:

```text
Sender:
attacker@example.xyz

URL:
https://example.xyz/login

IP:
203.0.113.10

Attachment:
invoice.docm
```

ThreatGraph correlates those indicators:

```text
EMAIL
 │
 ├── SENT_BY ───────► SENDER
 │                       │
 │                       ▼
 │                    DOMAIN
 │                       │
 │                       ▼
 │                      IP
 │
 ├── CONTAINS ──────► URL
 │                       │
 │                       ▼
 │                    DOMAIN
 │
 └── CONTAINS ──────► ATTACHMENT
                         │
                         ▼
                       HASH
```

This allows analysts to discover infrastructure shared by multiple suspicious emails.

---

# 3. ThreatGraph Entity Types

```text
EMAIL
EMAIL_ADDRESS
DOMAIN
URL
IP
ATTACHMENT
FILE_HASH
MESSAGE_ID
ASN
MAIL_SERVER
CAMPAIGN
THREAT_INTEL_OBSERVATION
```

Threat-intelligence observations can include:

```text
VirusTotal detection
urlscan finding
DNS result
WHOIS information
Blacklist result
SPF result
DKIM result
DMARC result
```

---

# 4. ThreatGraph Relationships

Examples:

```text
EMAIL
 ├── SENT_BY → EMAIL_ADDRESS
 ├── REPLIES_TO → EMAIL_ADDRESS
 ├── ROUTED_THROUGH → IP
 ├── CONTAINS → URL
 ├── CONTAINS → ATTACHMENT
 └── PART_OF → CAMPAIGN

DOMAIN
 ├── RESOLVES_TO → IP
 ├── HOSTS → URL
 └── IMPERSONATES → LEGITIMATE_DOMAIN

URL
 ├── REDIRECTS_TO → URL
 ├── HOSTED_ON → DOMAIN
 └── ASSOCIATED_WITH → IP

ATTACHMENT
 ├── HAS_HASH → SHA256
 └── DETECTED_AS → MALICIOUS_SAMPLE
```

Every relationship should store evidence and confidence.

---

# 5. Campaign Detection

ThreatGraph should identify shared infrastructure across multiple emails.

Example:

```text
Email 001
billing@fake-paypal.example

Email 002
support@fake-paypal.example

Email 003
security@fake-paypal.example
```

Common infrastructure:

```text
Domain:
fake-paypal.example

IP:
203.0.113.10

URL:
fake-paypal.example/login
```

MailXray creates:

```text
CAMPAIGN:
PAYMENT-PHISHING-001

Emails:
3

Shared Domains:
1

Shared IPs:
1

Shared URLs:
1

Campaign Confidence:
HIGH
```

---

# 6. Campaign Correlation Score

Initial model:

```text
Same sender domain       +20
Same Reply-To domain     +15
Same URL domain          +20
Same IP                  +20
Same attachment hash     +30
Same subject pattern     +10
Same infrastructure      +20
Same brand impersonation +15
```

Suggested interpretation:

```text
0–24     Weak relationship
25–49    Possible relationship
50–74    Likely campaign
75+      Strong campaign correlation
```

Example:

```text
Campaign Correlation Score: 82

Evidence:
+20 Same sender domain
+20 Same URL domain
+20 Same originating IP
+10 Similar subject pattern
+12 Same infrastructure

Assessment:
Strong campaign relationship
```

The exact weights should be configurable and validated against a labeled dataset.

---

# 7. Attack Chain Reconstruction

ThreatGraph should reconstruct the **observed or suspected** attack sequence.

Example:

```text
PHISHING EMAIL
       │
       ▼
SOCIAL ENGINEERING
       │
       ▼
MALICIOUS URL
       │
       ▼
CREDENTIAL-HARVESTING PAGE
       │
       ▼
POSSIBLE CREDENTIAL THEFT
       │
       ▼
POTENTIAL ACCOUNT TAKEOVER
```

Attachment-based example:

```text
PHISHING EMAIL
       │
       ▼
MALICIOUS ATTACHMENT
       │
       ▼
USER OPENS FILE
       │
       ▼
SCRIPT / MACRO EXECUTION
       │
       ▼
PAYLOAD
       │
       ▼
POTENTIAL C2
```

**Important:** observed evidence and inferred attack stages must be clearly separated.

For example:

```text
OBSERVED:
A credential-login page exists.

NOT CONFIRMED:
A user submitted credentials.
```

---

# 8. Evidence Confidence Engine

Risk and confidence must be separate.

## Confidence levels

```text
CONFIRMED
HIGH
MEDIUM
LOW
UNKNOWN
```

Example:

```text
Finding:
Malicious URL

Evidence:
- Multiple reputation detections
- Phishing indicators
- Credential-harvesting page

Confidence:
CONFIRMED
```

Another example:

```text
Finding:
Credential theft

Evidence:
Login page detected.

Missing:
Evidence that the victim entered credentials.

Confidence:
LOW

Status:
INFERRED — NOT CONFIRMED
```

This prevents unsupported conclusions.

---

# 9. Evidence Timeline

Every investigation should have a chronological audit trail.

```text
09:12:04  Email received
09:12:04  SHA-256 calculated
09:12:05  Headers parsed
09:12:05  SPF = FAIL
09:12:05  DKIM = FAIL
09:12:05  DMARC = FAIL
09:12:06  URLs extracted
09:12:07  IOCs extracted
09:12:12  VirusTotal queried
09:12:14  urlscan queried
09:12:18  ThreatGraph generated
09:12:20  Risk = HIGH
09:15:32  Analyst reviewed evidence
09:17:11  Final verdict = HIGH
```

---

# 10. Analyst Notes

Analysts should be able to record:

```text
Observation
Evidence
Hypothesis
Verification
Conclusion
```

Example:

```text
Observation:
Reply-To points to a different domain.

Hypothesis:
Possible phishing infrastructure.

Verification:
DNS and threat-intelligence checks performed.

Conclusion:
Reply-To domain is suspicious and is associated with
infrastructure found in another investigated email.
```

---

# 11. Complete Investigation Pipeline

```text
1. Upload Email
       ↓
2. Preserve Evidence
       ↓
3. Calculate SHA-256
       ↓
4. Parse Email
       ↓
5. Analyze Headers
       ↓
6. Analyze Sender
       ↓
7. Analyze Reply-To / Return-Path
       ↓
8. Check SPF / DKIM / DMARC
       ↓
9. Extract URLs
       ↓
10. Analyze URL Destinations
       ↓
11. Analyze Attachments
       ↓
12. Detect Social Engineering
       ↓
13. Extract IOCs
       ↓
14. Cross-Verify IOCs
       ↓
15. Calculate Risk
       ↓
16. Calculate Confidence
       ↓
17. Build ThreatGraph
       ↓
18. Correlate Campaigns
       ↓
19. Reconstruct Attack Chain
       ↓
20. Analyst Review
       ↓
21. Final Verdict
       ↓
22. Generate SOC Report
```

---

# 12. Email-by-Email Investigation

For every message analyze:

## Sender

- Display name
- Actual sender address
- Sender domain
- Display-name mismatch
- Domain mismatch
- Spoofing indicators
- Lookalike domains
- Typosquatting
- Unicode / IDN homographs
- Suspicious TLDs

## Reply-To

- Address
- Domain
- Relationship with From
- Reputation

## Return-Path

- Address
- Domain
- Relationship with sender
- Mail routing consistency

## Headers

- Message-ID
- Received chain
- Originating IP
- Mail servers
- Authentication-Results
- SPF
- DKIM
- DMARC
- ARC headers where available

## Content

- Urgency
- Fear
- Authority
- Reward
- Credential harvesting
- Financial requests
- Brand impersonation
- Suspicious language

## URLs

- Displayed text
- Actual href
- Domain
- IP
- Redirects
- Shorteners
- Suspicious paths
- Reputation

## Attachments

- Filename
- Extension
- MIME type
- Size
- SHA-256
- SHA-1
- MD5
- Macro presence
- Suspicious naming
- Reputation

---

# 13. Lookalike Domain Detection

Examples:

```text
Legitimate:
microsoft.com

Suspicious:
micros0ft.com
microsoft-login.com
microsoft-security.com
microsοft.com
microsoft-support.xyz
```

Detection techniques:

- Character substitution
- Character insertion
- Character deletion
- Character transposition
- Hyphen insertion
- Subdomain abuse
- Unicode homographs
- IDN abuse
- Suspicious TLDs
- Brand impersonation
- Levenshtein distance

---

# 14. URL Analysis

Never automatically click suspicious links on the analyst workstation.

Pipeline:

```text
Email
  │
  ▼
Extract URL
  │
  ├── Displayed Text
  ├── Actual HREF
  ├── Domain
  ├── TLD
  ├── IP
  ├── Port
  ├── Path
  ├── Query Parameters
  └── Redirect Information
```

Example:

```text
Displayed:
https://www.microsoft.com/security

Actual:
https://micros0ft-support.xyz/login

Findings:
- Displayed URL != actual destination
- Brand impersonation
- Suspicious domain
- Possible credential harvesting
```

---

# 15. Attachment Analysis

Attachments should be analyzed without executing them.

```text
Attachment
    │
    ├── Filename
    ├── Extension
    ├── MIME Type
    ├── Size
    ├── SHA-256
    ├── SHA-1
    ├── MD5
    └── Risk Indicators
```

High-risk extensions include:

```text
.exe
.scr
.bat
.cmd
.js
.vbs
.ps1
.hta
.lnk
.iso
.img
```

Macro-enabled Office files:

```text
.docm
.xlsm
.pptm
```

Suspicious naming examples:

```text
invoice.pdf.exe
payment_details.xlsm
urgent_payment.lnk
invoice.iso
password.zip
```

Do not execute suspicious attachments on the host system.

---

# 16. Social Engineering Detection

The platform should detect:

## Urgency

```text
Immediate action required
Respond within 30 minutes
Your account will be closed
Final warning
```

## Authority

```text
CEO
HR
IT Administrator
Bank
Government
Security Team
```

## Fear

```text
Account suspended
Unauthorized login detected
Legal action
Payment failure
Security breach
```

## Reward

```text
You've won
Claim your reward
Refund available
Bonus payment
Prize
```

## Credential Harvesting

```text
Verify your password
Confirm your account
Login immediately
Reset your credentials
```

The report must quote or reference the actual evidence found rather than making a vague claim.

---

# 17. IOC Extraction

Supported IOC types:

```text
EMAIL
DOMAIN
URL
IPV4
IPV6
FILE_NAME
MD5
SHA1
SHA256
MESSAGE_ID
ASN
```

IOC record:

```text
IOC
├── Type
├── Value
├── Source Email
├── Location
├── First Seen
├── Last Seen
├── Reputation
├── Confidence
├── Evidence
└── Verification Status
```

---

# 18. Threat Intelligence Layer

Use provider adapters:

```python
class ThreatIntelProvider:
    def check_domain(self, domain):
        pass

    def check_url(self, url):
        pass

    def check_ip(self, ip):
        pass

    def check_hash(self, sha256):
        pass
```

Potential providers:

```text
VirusTotal
urlscan.io
MXToolbox
Google Safe Browsing
DNS
WHOIS
```

Store:

```text
Provider
IOC
Timestamp
Result
Detection Count
Reputation
Raw Metadata
```

API keys must be stored using environment variables or a secrets manager.

---

# 19. Threat Intelligence Verification

Every suspicious IOC should have a verification record.

Example:

```text
IOC:
example.xyz

VirusTotal:
8 / 94 engines flag the domain

urlscan:
Phishing-related indicators detected

DNS:
Domain resolves to observed infrastructure

Final IOC Confidence:
HIGH
```

Threat intelligence is supporting evidence, not an automatic final verdict.

---

# 20. Risk Scoring

Initial scoring model:

```text
Sender mismatch             +15
Reply-To mismatch           +15
Return-Path anomaly         +10
SPF failure                 +10
DKIM failure                +10
DMARC failure               +15
Lookalike domain            +20
Suspicious URL              +20
URL mismatch                +20
Malicious attachment        +30
Malicious hash reputation   +40
Credential harvesting       +20
Urgency/fear language       +10
Known malicious IOC         +50
```

Suggested thresholds:

```text
0–19       LOW
20–39      MEDIUM
40–69      HIGH
70+        CRITICAL
```

Risk and confidence are separate dimensions:

```text
Risk:
CRITICAL

Confidence:
MEDIUM
```

This means the observed signals are dangerous but require further verification.

---

# 21. Dashboard

```text
┌─────────────────────────────────────────────────────────────┐
│ MAILXRAY                                      SOC CONSOLE   │
├─────────────────────────────────────────────────────────────┤
│ EMAILS       HIGH       CRITICAL       IOCs      CAMPAIGNS │
│  127          18            5           63           7     │
├─────────────────────────────────────────────────────────────┤
│ INVESTIGATION QUEUE                                        │
│                                                             │
│ ⚠ CEO Payment Request                 CRITICAL              │
│ ⚠ Microsoft Account Alert             HIGH                  │
│ ⚠ Invoice Attached                    HIGH                  │
│ ✓ LinkedIn Notification                LOW                  │
│ ? Password Expiration                  MEDIUM               │
├─────────────────────────────────────────────────────────────┤
│ THREATGRAPH                                                 │
│                                                             │
│         EMAIL                                               │
│           │                                                 │
│       ┌───┴───┐                                             │
│       ▼       ▼                                             │
│    DOMAIN    URL                                            │
│       │       │                                             │
│       └───┬───┘                                             │
│           ▼                                                 │
│           IP                                                │
└─────────────────────────────────────────────────────────────┘
```

---

# 22. Case Management

Each investigation receives a unique case ID.

Example:

```text
MSX-2026-00001
MSX-2026-00002
MSX-2026-00003
```

Case fields:

```text
Case ID
Title
Severity
Status
Assigned Analyst
Created At
Updated At
Affected Users
Related Emails
Related IOCs
Campaign
Analyst Verdict
Confidence
Evidence
Notes
```

Statuses:

```text
NEW
TRIAGED
INVESTIGATING
CONTAINMENT
RESOLVED
FALSE_POSITIVE
CLOSED
```

---

# 23. Database Design

## emails

```text
id
message_id
subject
sender
reply_to
return_path
received_at
raw_hash
risk_score
risk_level
confidence
verdict
case_id
```

## headers

```text
email_id
header_name
header_value
```

## urls

```text
email_id
displayed_url
actual_url
domain
ip
reputation
verdict
```

## attachments

```text
email_id
filename
mime_type
size
sha256
sha1
md5
verdict
```

## iocs

```text
email_id
type
value
source
location
evidence
confidence
verification_status
```

## threat_intel

```text
ioc_id
provider
query_time
result
detection_count
reputation
raw_response
```

## investigations

```text
email_id
analyst_verdict
automated_score
confidence
reasoning
created_at
updated_at
```

## campaigns

```text
id
name
description
confidence
created_at
updated_at
```

## campaign_members

```text
campaign_id
email_id
relationship_score
evidence
```

## graph_nodes

```text
id
node_type
value
metadata
created_at
```

## graph_edges

```text
id
source_node_id
target_node_id
relationship
confidence
evidence_id
created_at
```

---

# 24. Recommended Technology Stack

## Frontend

```text
React
TypeScript
Vite
Tailwind CSS
Recharts
Framer Motion
React Flow
```

## Backend

```text
Python
FastAPI
Pydantic
SQLAlchemy
```

## Email / Security Libraries

```text
Python email
mail-parser
dnspython
tldextract
BeautifulSoup
python-magic
hashlib
```

## NLP

```text
spaCy
NLTK
scikit-learn
```

## Database

```text
PostgreSQL
```

Optional graph database:

```text
Neo4j
```

## Infrastructure

```text
Docker
Docker Compose
GitHub Actions
Nginx
```

---

# 25. Project Structure

```text
mailxray/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── types/
│   │   └── graph/
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── analyzers/
│   │   │   ├── header_analyzer.py
│   │   │   ├── sender_analyzer.py
│   │   │   ├── url_analyzer.py
│   │   │   ├── attachment_analyzer.py
│   │   │   └── social_engineering.py
│   │   ├── threat_intel/
│   │   ├── scoring/
│   │   ├── threatgraph/
│   │   │   ├── graph_builder.py
│   │   │   ├── campaign_detector.py
│   │   │   └── attack_chain.py
│   │   └── reports/
│   ├── tests/
│   └── requirements.txt
│
├── samples/
│   ├── benign/
│   ├── phishing/
│   └── suspicious/
│
├── docs/
│   ├── architecture.md
│   ├── investigation-methodology.md
│   ├── threatgraph.md
│   └── api.md
│
├── docker/
├── .env.example
├── docker-compose.yml
├── README.md
└── LICENSE
```

---

# 26. Testing Strategy

Create a labeled test corpus containing:

```text
Benign emails
Marketing emails
Legitimate password resets
Known phishing samples
Invoice scams
CEO fraud
Credential phishing
Malicious attachment samples
Spoofed sender examples
Lookalike-domain examples
```

Test:

```text
Header parser
URL extractor
IOC extractor
Domain similarity
Social-engineering detector
Risk engine
Confidence engine
ThreatGraph
Campaign clustering
Attack-chain logic
Report generator
API endpoints
```

Measure:

```text
True Positives
True Negatives
False Positives
False Negatives
Precision
Recall
F1 Score
False Positive Rate
```

Performance metrics should always be calculated from actual test results and never hard-coded.

---

# 27. False Positive Management

Example:

```text
Automated Result:
HIGH

Analyst Review:
FALSE POSITIVE

Reason:
Sender belongs to an authorized third-party mail service.
SPF/DKIM alignment is valid for the organization's configuration.
```

The system should retain analyst overrides for future detection evaluation.

---

# 28. Security and Privacy Requirements

MailXray must be designed as a defensive analysis platform.

Never automatically:

- Execute suspicious attachments
- Open suspicious links on the analyst workstation
- Submit private email content to public services without authorization
- Store API keys in source control

Prefer:

```text
Static parsing
Hash analysis
Header analysis
DNS lookups
Reputation checks
Controlled URL scanning
Isolated malware analysis
```

When active URL scanning is used, it should be performed through an isolated analysis environment.

---

# 29. Evidence vs Inference

Every finding must have a status:

```text
OBSERVED
VERIFIED
CORRELATED
INFERRED
UNKNOWN
```

Example:

```text
Observed:
URL points to example.xyz/login

Verified:
Threat-intelligence service reports phishing indicators

Correlated:
Same domain appears in three investigated emails

Inferred:
Possible credential-harvesting campaign

Unknown:
Whether any user submitted credentials
```

This is a core design principle of MailXray.

---

# 30. Advanced Future Features

Potential future modules:

```text
STIX/TAXII export
SIEM integration
Splunk integration
Microsoft Sentinel integration
Elastic integration
SOAR integration
YARA-based attachment analysis
Sigma rule generation
MITRE ATT&CK mapping
Threat-intelligence feeds
User-risk scoring
Mailbox-wide IOC hunting
Automated containment recommendations
LLM-assisted analyst summaries
Detection-rule generation
Security regression testing
```

LLM functionality should assist analysts while preserving the underlying evidence and should never replace evidence-based investigation.

---

# 31. Development Roadmap

## Phase 1 — MVP

```text
✓ .eml upload
✓ Email parser
✓ Header extraction
✓ Sender analysis
✓ URL extraction
✓ Attachment extraction
✓ IOC extraction
✓ Basic risk scoring
✓ Investigation dashboard
```

## Phase 2 — Threat Intelligence

```text
✓ VirusTotal
✓ urlscan.io
✓ MXToolbox
✓ DNS
✓ WHOIS
✓ IP reputation
✓ Hash reputation
```

## Phase 3 — SOC Investigation

```text
✓ Evidence timeline
✓ Analyst notes
✓ Case management
✓ Analyst verdict override
✓ Confidence scoring
✓ Investigation reports
```

## Phase 4 — ThreatGraph

```text
✓ IOC relationship graph
✓ Email correlation
✓ Infrastructure correlation
✓ Campaign clustering
✓ Shared IOC detection
✓ Interactive graph visualization
✓ Attack-chain reconstruction
```

## Phase 5 — Advanced Detection

```text
✓ NLP social-engineering detection
✓ Lookalike-domain detection
✓ IDN homograph detection
✓ URL redirect analysis
✓ HTML analysis
✓ Attachment risk analysis
✓ Behavioral indicators
```

## Phase 6 — Professionalization

```text
✓ STIX/TAXII export
✓ JSON export
✓ CSV export
✓ REST API
✓ Authentication / RBAC
✓ Audit logs
✓ Docker
✓ CI/CD
✓ Unit tests
✓ Integration tests
✓ Detection performance evaluation
```

---

# 32. Portfolio Positioning

## Project Title

**MailXray — Email Threat Investigation, IOC Extraction & SOC Analysis Platform**

## Advanced Feature

**ThreatGraph — Email Attack Graph & Campaign Attribution Engine**

## One-Line Description

> A SOC-oriented email security platform that performs email forensics, IOC extraction, threat-intelligence verification, evidence correlation, risk assessment, phishing campaign discovery, and explainable attack-chain analysis.

## Skills Demonstrated

```text
Email Security
SOC Analysis
Phishing Investigation
Threat Intelligence
IOC Extraction
OSINT
SPF / DKIM / DMARC
Email Header Analysis
URL Analysis
Malware Triage
Risk Assessment
Incident Response
Threat Correlation
Campaign Detection
Attack-Chain Analysis
Digital Forensics
Python
FastAPI
React
PostgreSQL
REST APIs
Docker
```

---

# 33. Final Project Objective

MailXray should demonstrate the complete workflow of a modern email-security investigation:

```text
             SUSPICIOUS EMAIL
                    │
                    ▼
              PRESERVE EVIDENCE
                    │
                    ▼
              FORENSIC ANALYSIS
                    │
                    ▼
               IOC EXTRACTION
                    │
                    ▼
             THREAT INTELLIGENCE
                    │
                    ▼
             EVIDENCE CORRELATION
                    │
                    ▼
                THREATGRAPH
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
      CAMPAIGN             ATTACK
      ANALYSIS             CHAIN
          │                   │
          └─────────┬─────────┘
                    ▼
              RISK SCORING
                    │
                    ▼
             ANALYST REVIEW
                    │
                    ▼
              FINAL VERDICT
                    │
                    ▼
               SOC REPORT
```

## Core Principle

> **Evidence first. Correlation second. Verdict last.**

The system must never present an assumption as a confirmed fact.
