# Virtual Patient Simulator for Dentistry Capabilities

This simulator is a web-based virtual patient training platform for dental students. It guides learners through history-taking, clinical examination, and investigation phases using interactive 3D intraoral and extraoral models with real-time OSCE-aligned scoring and formative feedback. It targets low-cost VR delivery with no haptic hardware.

## History-Taking

- Students select question categories and individual questions covering presenting complaint, medical history, habits, oral hygiene, dietary patterns, prior treatments, and social context
- Question ordering and relevance are tracked and scored

## Clinical Examination

- 3D intraoral and extraoral models support zoom, rotation, and tool selection for soft and hard tissue assessment
- Plaque scores and bleeding scores are calculated from examination-phase interactions
- Caries and restoration identification is evaluated against case-specific ground truth

## Investigation

- Students select radiographic views (panoramic, periapical, bitewing, CBCT) and hematological or sensibility tests appropriate to the case

## Assessment

- OSCE-aligned numeric scoring on a 1-to-100 scale evaluates each training phase
- An intelligent tutoring module provides real-time feedback on question choice, tool selection, and clinical findings

## Constraints

- No haptic or force-feedback hardware integration; targets low-cost browser-based VR
- Web-only delivery built primarily in JavaScript; no native desktop or mobile application
- Validated with a 33-student trial that did not show statistically significant OSCE score improvement over controls
- No documented API, authentication system, or learning management system integration
- No Docker, CI/CD pipeline, or automated tests
