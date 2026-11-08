# Lab 2a Report — Human-Guided AI Analysis in an Agentic SOC

**Date:** November 8, 2026  
**Lab:** Morpheus Lite Agentic SOC  
**Group Members:** Roy Tevel - רואי טבל | Lior Levin - ליאור לווין  

---

## Part A & B — Environment Setup

The lab environment was set up successfully. Docker Desktop was running with Redpanda (Kafka-compatible broker) on port 19092 and Redpanda Console on port 18080. Python dependencies were installed in a virtual environment and all 6 tests passed before starting.

The following services were launched in separate terminals:
- **Redpanda** — message streaming platform
- **Detector** (`morpheus_lite_detector.py`) — Isolation Forest + fingerprinting
- **Agent Orchestrator** (`agent_orchestrator.py`) — threat hunting, RAI, XAI, Meta-AI
- **Telemetry Generator** (`telemetry_generator.py`) — produces synthetic security events
- **Dashboard** (`dashboard.py`) — Streamlit UI on port 8501

---

## Part C — Event Flow & Case Identification

After fetching cases from Kafka, the dashboard showed **43 total cases**, of which **21 were high risk** and **21 were pending human review**.

![Dashboard overview showing 43 cases fetched from Kafka](photos/צילום%20מסך%202026-11-08%20ב-18.25.26.png)

The selected case for analysis:

| Field | Value |
|-------|-------|
| `alert_id` | alert-0-9 |
| `correlation_id` | 9528a1ff-0b16-4a9d-bf5f-4e2b97ce2294 |
| event type | suspicious_process |
| host | web-01 |
| user | svc-backup |
| risk score | 100 |

**Question C1 — Why use alert_id vs correlation_id?**

The `alert_id` is used in the dashboard to select and display a specific case. The `correlation_id` is a backend identifier that links the same event across all Kafka topics and agent outputs — it lets you trace one alert from raw telemetry all the way to the final human decision. They serve different purposes: one is for the user interface, the other is for backend tracing.

---

## Part D — Case Selection & Synchronization

The case `alert-0-9` was selected using the checkbox in the All Cases table. The same `alert_id` appeared in the Active Alert bar, the Human Decision Queue, and the Case Details panel — confirming that all three sections were synchronized.

![All Cases table with alert-0-9 selected](photos/צילום%20מסך%202026-11-08%20ב-18.26.17.png)

---

## Part E — Case Analysis

### E1. Detection Evidence

| Evidence | Observation |
|----------|-------------|
| event type | suspicious_process |
| failed logins | 30 (high) |
| outbound bytes | 38,055,230 (~38 MB) |
| process count | 150 (abnormally high) |
| geographic indicator | Country: IR (outside normal profile) |
| fingerprint deviation | z=0 (no historical profile for this user yet) |
| Isolation Forest result | -1 (anomalous) |

### E2. XAI Explanation

**What triggered the alert?**
The combination of a suspicious process type, high failed logins, large outbound transfer, abnormal process count, and a login from a country outside the normal profile all together triggered the alert.

**Strongest evidence?**
The failed logins (30) combined with the large data transfer (~38 MB outbound) are the strongest indicators. Together they suggest credential abuse followed by data exfiltration.

**Does the explanation match the evidence?**
Yes — the XAI explanation accurately lists all six evidence items and links them to the risk score of 100.

**Does it overstate certainty?**
Slightly. The fingerprint z-score is 0, meaning there is no historical baseline for this user. The XAI doesn't flag this limitation clearly.

**What evidence is missing?**
Endpoint logs from web-01, the specific process name that ran, and confirmation from a SIEM or EDR tool.

### E3. RAI Policy

| Field | Value |
|-------|-------|
| recommended action | recommend_isolation_with_human_approval |
| action allowed | true |
| human approval required | true |
| policy rationale | High risk. Isolation may be recommended, but human approval is required. |

### E4. Meta-AI Review

| Field | Value |
|-------|-------|
| disposition | approve |
| approved | true |
| issues | none |
| questions or requests | none |
| uncertainty | 0 |
| reflection | Decision is sufficiently supported for governed continuation. |

![Case details showing XAI, Evidence, RAI Decision, and Meta-AI Review](photos/צילום%20מסך%202026-11-08%20ב-18.28.00.png)

![Full case details panel](photos/צילום%20מסך%202026-11-08%20ב-18.29.15.png)

---

## Part F — Human Decision

**Decision: `approve`**

**Justification:**

I approve the recommendation because the alert is backed by six separate indicators: 30 failed login attempts, ~38 MB of outbound data transfer, 150 running processes, a login from Iran (outside the normal profile), a suspicious process event type, and an Isolation Forest anomaly flag. These are independent signals that all point in the same direction — a service account that is likely compromised and may be exfiltrating data. The proposed action (isolation with human approval) is proportionate to a risk score of 100. The RAI policy is working correctly by requiring a human to authorize the action before anything is executed. The Meta-AI review found no logical issues with the recommendation. Some uncertainty remains because the user fingerprint has no historical baseline yet, but the other evidence is strong enough to justify the decision.

---

## Part G — Decision Verification

### G2. Kafka Verification

The human decision was confirmed in the `human.decisions` Kafka topic with 1 message recorded at 8.11.2026, 18:28:49. The value starts with `{"alert_id":"alert-0-9","correlati...` confirming the correct record was written.

![Redpanda Console showing human.decisions topic with 1 message](photos/צילום%20מסך%202026-11-08%20ב-18.30.03.png)

### G3. Audit File Verification

The `data/audit.jsonl` file was checked using grep. The file contained the full case record for `alert-0-9` including the human decision entry with:
- `decision: approve`
- `risk_score: 100`
- `rai_recommendation: recommend_isolation_with_human_approval`
- `meta_ai_disposition: approve`

---

## Part H — Research Export

The export script ran successfully:

```
Exported 161 records to exports/morpheus_lite_20261108_163236.parquet
```

The exported Parquet file contains 161 audit records. Each record can be linked across pipeline stages using `alert_id` and `correlation_id`.

---

## Part I — Reflection

**1. Did my decision agree with the AI recommendation?**  
Yes. The AI recommended isolation with human approval, and I approved it. The six independent evidence items gave me enough confidence to agree with the recommendation.

**2. Which evidence had the greatest influence?**  
The combination of 30 failed logins and 38 MB outbound transfer was the most convincing. Each one alone could have an innocent explanation, but together they strongly suggest credential abuse followed by data exfiltration.

**3. What did the XAI explanation help me understand?**  
It gave a clear picture of which individual signals were contributing to the high risk score. Without it, I would have had to piece together the evidence manually from raw fields.

**4. What part of the explanation did I challenge?**  
The explanation did not mention that the fingerprint z-score was 0, which means there is no historical behavior baseline for `svc-backup`. That's an important limitation — the behavioral anomaly detection is essentially blind for this user at this point.

**5. What additional evidence would improve confidence?**  
Endpoint logs from web-01 showing what the suspicious process actually was, network flow data showing the destination of the 38 MB transfer, and confirmation from an EDR or SIEM tool.

**6. How did the RAI policy affect the decision?**  
The policy prevented any automated action. Even though the risk score was at the maximum, the system required a human to authorize isolation. This is the right design — an automated isolation of a service account could disrupt legitimate operations if the alert turned out to be a false positive.

**7. Did the Meta-AI review make me more or less willing to rely on the recommendation?**  
Slightly more. It confirmed that the logic was internally consistent and found no issues. But it's worth noting that the Meta-AI is checking for logical consistency, not validating the raw telemetry. It would still approve a well-structured case built on wrong data.

**8. Who retained final decision authority?**  
The human analyst. The AI pipeline generated a recommendation, but no action was taken until the analyst reviewed the evidence and submitted a decision. That is the correct model for high-risk actions.

---

## Submission Checklist

- [x] Case identification table
- [x] Evidence analysis
- [x] XAI evaluation
- [x] RAI and Meta-AI review
- [x] Human decision with justification
- [x] Kafka verification
- [x] Audit file verification
- [x] Research export verification
- [x] Reflection answers
