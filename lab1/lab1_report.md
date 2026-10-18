# Lab 1 | From CTI to SOC Investigation and MITRE ATT&CK Mapping

**Course:** Introduction to Cybersecurity  
**Group Members:** Roy Tevel, Lior Levin

---

## Step 1 | Select a CTI Report

**Title:** Ongoing Targeted Campaign Against US Law Firms  
**Publisher:** Google Threat Intelligence (Mandiant / GTIG)  
**Publication Date:** 2026  
**URL:** https://cloud.google.com/blog/topics/threat-intelligence/targeted-campaign-us-law-firms

### Attack Summary

Between January and May 2026, the threat actor UNC3753 (also known as Luna Moth, Chatty Spider, and Silent Ransom Group) conducted a financially motivated data theft and extortion campaign targeting dozens of U.S. law firms and financial services organizations.

The attackers began by sending invoice-themed emails from consumer accounts containing no links or attachments — designed solely to plant concern and establish a pretext. They then followed up with phone calls impersonating internal IT helpdesk staff, convincing targets to initiate screen-sharing sessions via tools such as Zoom or Microsoft Teams. Once visual access was established, the attackers directed victims to install Remote Monitoring and Management (RMM) tools such as AnyDesk or Zoho Assist, granting persistent remote access. Using that access, they searched for and exfiltrated sensitive legal documents, often completing the entire attack within a single business day. In some cases, operatives physically entered offices to extract data via USB storage devices.

---

## Step 2 | Extract Behaviors and Draw the Attack Flow

### Attack Flow Diagram

```
╔══════════════════════════════════════════════╗
║  📧  INITIAL ACCESS                          ║
║      Invoice-Themed Email (no attachment)    ║
║      Pretext to establish concern            ║
╚══════════════════════════╦═══════════════════╝
                           ║
                           ▼
╔══════════════════════════════════════════════╗
║  📞  SOCIAL ENGINEERING                      ║
║      Vishing — IT Helpdesk Impersonation     ║
║      Follow-up phone call                    ║
╚══════════════════════════╦═══════════════════╝
                           ║
                           ▼
╔══════════════════════════════════════════════╗
║  🖥️  REMOTE ACCESS                           ║
║      Screen Sharing Session                  ║
║      Zoom / Microsoft Teams / Quick Assist   ║
╚══════════════════════════╦═══════════════════╝
                           ║
                           ▼
╔══════════════════════════════════════════════╗
║  ⚙️  PERSISTENCE & C2                        ║
║      RMM Tool Installation                   ║
║      AnyDesk / Zoho Assist / Bomgar          ║
╚══════════════════════════╦═══════════════════╝
                           ║
                           ▼
╔══════════════════════════════════════════════╗
║  🔍  COLLECTION                              ║
║      File Search & Staging                   ║
║      Sensitive legal documents located       ║
╚══════════════════════════╦═══════════════════╝
                           ║
                           ▼
╔══════════════════════════════════════════════╗
║  📤  EXFILTRATION                            ║
║      Remote transfer via RMM session         ║
║      Physical USB intrusion (some cases)     ║
╚══════════════════════════╦═══════════════════╝
                           ║
                           ▼
╔══════════════════════════════════════════════╗
║  ⚠️  IMPACT                                  ║
║      Data Theft & Extortion                  ║
║      Ransom demand (up to $20M)              ║
╚══════════════════════════════════════════════╝
```

### Observed Behaviors

| # | Behavior | Source in Report | Observed / Inferred |
|---|----------|-----------------|---------------------|
| 1 | Invoice-themed email sent to establish pretext | Explicitly described | Observed |
| 2 | Phone call impersonating IT helpdesk (Vishing) | Explicitly described | Observed |
| 3 | Screen-sharing session via Zoom / Teams / Quick Assist | Explicitly described | Observed |
| 4 | Installation of RMM tools (AnyDesk, Zoho Assist, Bomgar) | Explicitly described | Observed |
| 5 | Search and staging of sensitive legal files | Described in report | Observed |
| 6 | Data exfiltration (remote transfer or physical USB) | Explicitly described | Observed |

---

## Step 3 | Map Behaviors to ATT&CK

| Observed Behavior | ATT&CK Tactic | Technique / ID | Evidence & Rationale | SOC Telemetry / Investigation |
|-------------------|--------------|----------------|----------------------|-------------------------------|
| Invoice-themed phishing email | Initial Access | Phishing: Spearphishing via Service (T1566.003) | Report describes invoice emails from consumer accounts with no payload, used to establish pretext | Email gateway logs; flag messages from consumer domains impersonating vendors |
| Vishing — IT impersonation phone call | Initial Access | Phishing: Vishing (T1566.004) | Report explicitly states callers posed as internal IT helpdesk | No direct log source; correlate with subsequent RMM install events as a signal |
| Screen sharing via Zoom / Teams / Quick Assist | Command & Control | Remote Access Software (T1219) | Report explicitly names these tools as used in attack | Process creation logs; alert on unexpected screen-sharing apps launched by non-IT users |
| RMM tool installation (AnyDesk / Zoho / Bomgar) | Persistence / C2 | Remote Access Software (T1219) | Report explicitly names AnyDesk, Zoho Assist, Bomgar, SuperOps | EDR alert on RMM binary installation; check parent process and user context |
| File search for sensitive legal documents | Collection | Data from Local System (T1005) | Report describes attackers searching and staging files | File access logs; EDR alert on mass file reads from legal document directories |
| Data exfiltration via remote transfer or USB | Exfiltration | Exfiltration Over C2 Channel (T1041) / Exfiltration over Physical Medium (T1052) | Report describes both remote exfil and physical USB intrusions | DLP alerts on large outbound transfers; USB device logs on endpoints |

---

## Step 4 | Connect the Mapping to SOC Investigation

### Behavior 3 — RMM Tool Installation (T1219)

**Tier 1 Analyst:**
- Review EDR alert triggered by installation of AnyDesk or Zoho Assist
- Check if the installing user belongs to the IT/helpdesk group
- Flag if installation followed an email from an external consumer domain

**Tier 2 Analyst:**
- Investigate the parent process that launched the installer
- Review screen-sharing and remote session logs around the same timeframe
- Correlate with email logs to reconstruct the social engineering chain

---

### Behavior 5 — File Search & Staging (T1005)

**Tier 1 Analyst:**
- Review file access alerts showing mass reads of sensitive directories
- Note the user account and workstation involved
- Check if behavior occurred during or after a remote session

**Tier 2 Analyst:**
- Identify which files were accessed and whether any were copied or moved
- Cross-reference with network logs for outbound transfers
- Determine if the RMM session was active at the time

---

### Behavior 6 — Data Exfiltration (T1041 / T1052)

**Tier 1 Analyst:**
- Review DLP alert for large outbound data transfer
- Check destination IP/domain against threat intelligence feeds
- Escalate if transfer occurred via an active RMM session

**Tier 2 Analyst:**
- Reconstruct full attack timeline from initial email to exfiltration
- Identify the volume and type of data exfiltrated
- Notify legal and compliance teams given the sensitive nature of stolen documents

---

## Step 5 | Discuss and Review

**Behavior in question:** The initial invoice-themed email (no links, no attachments)

**Current Mapping:** T1566.003 — Phishing: Spearphishing via Service

**Alternative Interpretation:** This email alone does not constitute a technical attack — it is purely social manipulation with no payload. It could be argued that it does not map to any ATT&CK technique independently, and only becomes relevant as part of the vishing chain (T1566.004).

**Evidence needed to resolve:**
- Confirmation that the email was specifically crafted to target the individual (spearphishing vs. bulk)
- Evidence that the email was sent through a third-party service rather than directly
- Clarification of whether ATT&CK considers a purely pretextual email (no malicious content) as phishing

---

*Report analysis based on: Google Threat Intelligence — https://cloud.google.com/blog/topics/threat-intelligence/targeted-campaign-us-law-firms*
