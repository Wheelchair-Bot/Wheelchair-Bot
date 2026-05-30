# FDA Q-Submission (pre-submission) — template

For the US FDA Q-Submission program — formal feedback before a 510(k)
or De Novo submission. Reference: FDA guidance "Requests for Feedback
and Meetings for Medical Device Submissions" (2023).

> ⚠️ Template only. Final submission owned by regulatory counsel.

## 1. Background

Wheelchair-Bot is a retrofit tele-operation system for commercially
available powered wheelchairs. The host chair is a class II device
(21 CFR 890.3700). Our retrofit adds:

- Compute + sensors (comma 3X)
- A CAN-bus adapter (one of: R-Net, Shark/DX, VR2)
- Smartphone / web tele-op client
- Software safety layers

## 2. Regulatory questions for FDA

1. Does this retrofit re-classify the host chair, or remain a class II
   accessory under 21 CFR 890.3700?
2. Is a De Novo submission preferred over 510(k) given the lack of a
   direct predicate for tele-operation of a powered wheelchair?
3. Are the proposed software risk-controls (dual watchdog, hardware
   e-stop relay, panda safety mode) adequate per the Software in a
   Medical Device (SaMD) guidance?
4. Will the comma 3X compute platform require its own component-level
   submission, or can it be qualified as a sub-system?
5. What clinical evidence is expected for class II tele-operation
   (literature review vs. small pivotal study)?

## 3. Proposed indications for use

Wheelchair-Bot is intended for **assisted tele-operation** of a
compatible commercial powered wheelchair by a designated remote driver
under continuous supervision of the rider or rider's caregiver, in
indoor and sidewalk environments. The system is not intended for
unsupervised autonomous operation, public-road use, or any use case
outside the operational design domain in [risk_file.md](risk_file.md).

## 4. Pre-submission package contents (planned)

- Cover letter
- Risk file ([risk_file.md](risk_file.md)) expanded by consultant
- Software description per FDA SaMD guidance
- IEC 60601-1 + ISO 7176-14 compliance plan
- Cybersecurity plan per FDA 2023 final guidance (auth, OTA signing)
- Labelling drafts
- Verification & validation plan summary
