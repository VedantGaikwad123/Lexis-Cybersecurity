### 1. Executive Summary

Financial institutions face increasing threats from SIM-swap and SIM-cloning attacks, where fraudsters impersonate customers during mobile/internet banking registration to intercept OTPs, steal credentials, and divert funds. This proposal outlines a **multi-factor, risk-scored approach** leveraging device and SIM identifiers (IMEI, ICCID, Android ID/IDFA), location consistency, and behavioral analytics to accurately flag high-risk registration attempts while minimizing friction for legitimate users.

---

### 2. Problem Statement

- **Impersonated Registrations**: Fraudsters initiate mobile/internet banking registration on cloned or swapped SIMs, obtaining OTPs and credentials.
    
- **SIM-Level Cloning**: Techniques such as SIM swap fraud and 'smishing' enable attackers to duplicate IMSI and MSISDN onto a new physical SIM.
    
- **Detection Gaps**: Traditional methods rely on OTP confirmation and basic IP/location checks, yielding high false-positive or -negative rates.
    

> **Objective**: Design a practical solution to distinguish genuine customer registrations from fraudster-initiated registrations, using client-reported device/SIM metadata and server-side correlation.

---

### 3. Proposed Solution Overview

**Core Idea**: Compare historical user–device/SIM bindings against incoming registration metadata. Unexpected pairings (e.g., same IMSI on new IMEI, new ICCID, or abnormal geo-distance) increment a **risk score**. Registrations are auto-approved, step-up authenticated, or blocked based on score thresholds.

**Key Signals**:

1. **Device Identifiers**
    
    - **IMEI** (Android) / **IDFA** (iOS)
        
    - **Android ID** (fallback on Android)
        
2. **SIM Identifiers**
    
    - **ICCID** (SIM serial number)
        
    - **IMSI** (subscriber identity)
        
3. **Location Consistency**
    
    - GPS or network-based location vs. user’s recent registration footprints
        
4. **Behavioral Biometrics**
    
    - Typing/swipe dynamics, app-usage patterns
        

---

### 4. Technical Approach

#### 4.1 Mobile SDK Data Collection

|Data Point|Android Method|iOS Method|Notes|
|---|---|---|---|
|IMEI|`TelephonyManager.getImei()`|✕ Not available|Android 10+ requires privileged permission|
|ICCID|`getSimSerialNumber()`|✕ Not available|Unique per physical SIM|
|Android ID|`Settings.Secure.ANDROID_ID`|n/a|Persisted until factory reset|
|IDFA / IDFV|n/a|`ASIdentifierManager`|Requires user opt-in (ATT)|
|IMSI|`getSubscriberId()`|✕ Not available|May be restricted on Android 10+|
|Location|`FusedLocationProviderClient`|`CLLocationManager`|Requires runtime consent|
|Behavioral Data|Touch-event hooks + local ML inference|Gesture/Touch APIs + local ML|Privacy-friendly, opt-in|

- **Data Security**: All identifiers are hashed (e.g., SHA-256) on-device before transit. Payloads are signed using the app’s certificate key to ensure integrity.
    

#### 4.2 Backend Risk Engine

1. **Ingestion API**: Verifies signature, decrypts payload.
    
2. **Historical Lookup**: Retrieves the user’s previous device–SIM records.
    
3. **Signal Comparison**: Computes per-signal deltas (e.g., IMEI change = +30 risk points).
    
4. **Risk Scoring**:
    
    |Signal|Delta Condition|Risk Weight|
    |---|---|--:|
    |IMEI mismatch|New IMEI vs. historical|+30|
    |ICCID mismatch|New SIM vs. historical|+30|
    |Android ID/IDFA new|New vs. stored identifier|+20|
    |Geo-distance|>50 km from last register|+10|
    |Behavioral anomaly|Deviation above threshold|+10|
    
5. **Decision Logic**:
    
    - **Auto-Approve**: Total score < 30
        
    - **Step-Up**: 30 ≤ score < 60 (e.g., video verification, OTP+voice confirmation)
        
    - **Block/Manual Review**: score ≥ 60
        

#### 4.3 Monitoring & Alerting Dashboard

- **Real-Time Alerts**: Highlight when the same IMSI is seen on two different IMEIs within 24 hrs.
    
- **Fraud Ops View**: Dashboard filtering by high-risk registrations, location anomalies, repeated failures.
    

---

### 5. Implementation Roadmap

|Phase|Tasks|Timeline|
|---|---|---|
|**Phase 1**|Build Mobile SDK (Android + iOS fallback) + Basic API|4 weeks|
|**Phase 2**|Develop Backend Risk Engine + datastore design|3 weeks|
|**Phase 3**|Integrate Step-Up flows; root/jailbreak detection|2 weeks|
|**Phase 4**|Monitoring Dashboard + Alert Rules|2 weeks|
|**Phase 5**|Privacy review, compliance checks (GDPR/TRAI), performance tuning|3 weeks|

---

### 6. Privacy, Security & Compliance

- **Consent & Transparency**: Disclose data collection in the app’s privacy policy; request runtime permissions with clear justification.
    
- **Data Minimization**: Store only hashed identifiers; purge records after 12 months of inactivity.
    
- **Regulatory Adherence**:
    
    - **India**: TRAI and RBI guidelines for customer data.
        
    - **EU/US**: GDPR/CCPA where applicable.
        
- **Security**: TLS encryption in transit; AES-256 at rest; regular security audits.
    

---

### 7. Limitations & Mitigations

|Limitation|Mitigation|
|---|---|
|**Android 10+ privileged ID access**|Fallback to Android ID; encourage OS-level partner integration|
|**Spoofing on rooted/jailbroken devices**|Root/jailbreak detection; SafetyNet/DeviceCheck attestation|
|**Dual‑SIM ambiguity**|Query both slots; require explicit SIM selection by user|
|**iOS identifier gap**|Leverage IDFA/IDFV + device fingerprinting & behavior|
|**False positives on new devices**|User self‑service to confirm device change; risk weighting|

---

### 8. Conclusion

By implementing this **layered, risk‑scoring solution**, banks can significantly improve fraud detection during mobile/internet registration—catching SIM cloning attacks early—while preserving a frictionless UX for legitimate users. The approach balances **effectiveness**, **privacy**, and **scalability**, making it a strong candidate for production deployment.

ity**: TLS encryption in transit; AES-256 at rest; regular security audits.
    

---

### 7. Limitations & Mitigations

|Limitation|