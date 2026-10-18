# Lab 1 | From CTI to SOC Investigation and MITRE ATT&CK Mapping

**Course:** Introduction to Cybersecurity  
**Group Members:** Roy Tevel, Lior Levin

---

## 1 | CTI Report Citation

**Title:** Ongoing Targeted Campaign Against US Law Firms  
**Publisher:** Google Threat Intelligence (Mandiant / GTIG)  
**Publication Date:** 2026  
**URL:** https://cloud.google.com/blog/topics/threat-intelligence/targeted-campaign-us-law-firms

---

## 2 | Attack Summary

Between January and May 2026, the threat actor UNC3753 (also known as Luna Moth, Chatty Spider, and Silent Ransom Group) conducted a financially motivated data theft and extortion campaign targeting dozens of U.S. law firms and financial services organizations.

The attackers began by sending invoice-themed emails from consumer accounts containing no links or attachments — designed solely to plant concern and establish a pretext. They then followed up with phone calls impersonating internal IT helpdesk staff, convincing targets to initiate screen-sharing sessions via tools such as Zoom or Microsoft Teams. Once visual access was established, the attackers directed victims to install Remote Monitoring and Management (RMM) tools such as AnyDesk or Zoho Assist, granting persistent remote access. Using that access, they searched for and exfiltrated sensitive legal documents, often completing the entire attack within a single business day. In some cases, operatives physically entered offices to extract data via USB storage devices.

---

## 3 | Attack Flow Diagram

```
Invoice-Themed Email (No attachment)
        |
        v
Follow-up Phone Call (Vishing / IT Impersonation)
        |
        v
Screen Sharing Session (Zoom / Teams / Quick Assist)
        |
        v
RMM Tool Installation (AnyDesk / Zoho Assist / Bomgar)
        |
        v
File Search & Staging (Sensitive legal documents)
        |
        v
Data Exfiltration (Remote transfer or USB physical intrusion)
        |
        v
Extortion / Ransom Demand
```

---

## 4 | Observed Behaviors

| # | Behavior | Source in Report | Observed / Inferred |
|---|----------|-----------------|---------------------|
| 1 | Invoice-themed email sent to establish pretext | Explicitly described | Observed |
| 2 | Phone call impersonating IT helpdesk (Vishing) | Explicitly described | Observed |
| 3 | Screen-sharing session via Zoom / Teams / Quick Assist | Explicitly described | Observed |
| 4 | Installation of RMM tools (AnyDesk, Zoho Assist, Bomgar) | Explicitly described | Observed |
| 5 | Search and staging of sensitive files | Described in report | Observed |
| 6 | Data exfiltration (remote or via USB physical intrusion) | Explicitly described | Observed |

---

## 5 | ATT&CK Mapping Table

| Observed Behavior | ATT&CK Tactic | Technique / ID | Evidence & Rationale | SOC Telemetry / Investigation |
|-------------------|--------------|----------------|----------------------|-------------------------------|
| Invoice-themed phishing email | Initial Access | Phishing: Spearphishing via Service (T1566.003) | Report describes invoice emails sent from consumer accounts with no links/attachments to establish pretext | Email gateway logs; flag messages from consumer domains (gmail, yahoo) impersonating vendors |
| Vishing — IT impersonation phone call | Social Engineering | Phishing: Vishing (T1566.004) | Report explicitly states callers posed as internal IT helpdesk | No direct log source; correlate with subsequent RMM install events as a signal |
| Screen sharing via Zoom / Teams / Quick Assist | Remote Access | Remote Access Software (T1219) | Report explicitly names these tools as used in attack | Process creation logs; alert on unexpected launch of screen-sharing apps by non-IT users |
| RMM tool installation (AnyDesk / Zoho / Bomgar) | Persistence / Command & Control | Remote Access Software (T1219) | Report explicitly names AnyDesk, Zoho Assist, Bomgar, SuperOps | EDR alert on RMM binary installation; check parent process and user context |
| File search for sensitive legal documents | Collection | Data from Local System (T1005) | Report describes attackers searching and staging files | File access logs; EDR alert on mass file reads from legal document directories |
| Data exfiltration via remote transfer or USB | Exfiltration | Exfiltration Over C2 Channel (T1041) / Exfiltration over Physical Medium (T1052) | Report describes both remote exfil and physical USB intrusions | DLP alerts on large outbound transfers; USB device logs on endpoints |

---

## 6 | SOC Investigation Notes

### Behavior 3 — RMM Tool Installation (T1219)

**Tier 1 Analyst:**
- Review EDR alert triggered by installation of AnyDesk or Zoho Assist
- Check if the installing user is in IT/helpdesk group
- Flag if installation followed an email from an external consumer domain

**Tier 2 Analyst:**
- Investigate parent process that launched the installer
- Review screen-sharing and remote session logs around the same timeframe
- Correlate with email logs to reconstruct the social engineering chain

---

### Behavior 5 — File Search & Staging (T1005)

**Tier 1 Analyst:**
- Review file access alerts showing mass reads of sensitive directories
- Note the user account and workstation involved
- Check if behavior occurred during or after a remote session

**Tier 2 Analyst:**
- Identify which files were accessed and whether any were copied/moved
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
- Notify legal and compliance teams given sensitive nature of stolen documents

---

## 7 | Uncertain Mapping

**Behavior:** The initial invoice-themed email (no links, no attachments)

**Current Mapping:** T1566.003 — Phishing: Spearphishing via Service

**Alternative Interpretation:** This email alone does not constitute a technical attack — it is purely social manipulation with no payload. It could be argued this does not map to any ATT&CK technique independently, and only becomes relevant as part of the vishing chain (T1566.004).

**Evidence needed to resolve:**
- Confirmation that the email was specifically crafted to target the individual (spearphishing)
- Evidence that the email was sent through a third-party service rather than directly
- Whether ATT&CK considers a purely pretextual email (no malicious content) as phishing

---

*Report analysis based on: Google Threat Intelligence — https://cloud.google.com/blog/topics/threat-intelligence/targeted-campaign-us-law-firms*
