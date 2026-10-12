# Hritika Adhikary · Biomedical Engineering Portfolio

**Medical imaging & AI · Biomechanics · Patient-specific design · Wearable systems**

I am a biomedical engineer who works across computational models, medical images, and physical devices. This portfolio brings together my academic projects, professional contributions, and software development work.

[Featured projects](#featured-projects) · [Explore by field](#explore-by-field) · [Software projects](#software-projects) · [Experience](#experience) · [Certifications](#certifications) · [LinkedIn](https://www.linkedin.com/in/hritika-adhikary-58179a1b6/)

## Featured projects

### 01 · Medical image analysis
**Arizona State University · Dr. Jianming Liang · Fall 2025**

**The problem:** Extract useful information from chest X-rays through classification, segmentation, and lesion localization.

**My contribution:** I prepared image inputs and masks, built PyTorch pipelines, and ran GPU experiments on ASU’s Sol cluster. My work included U-Net, UPerNet with ResNet-101, and Faster R-CNN with ResNet50-FPN.

**Selected outcomes:**
- Approximately **0.89 Dice** for lung segmentation.
- **95% classification accuracy** in the experiment reported on my résumé.
- **0.43 Dice / 0.27 IoU** in a separate UPerNet multi-class segmentation experiment.
- A **30-epoch** NODE21 detection training run with monitored convergence.

These results describe separate experiments, not a single combined benchmark.

**Status:** Reported academic experiments completed. The public repository contains metric utilities, tests, and a SLURM template; dataset-specific training notebooks and weights are not currently published.

[Explore the project](https://github.com/hrix7/Medical-Imaging-Deep-Learning) · [Metric utilities](https://github.com/hrix7/Medical-Imaging-Deep-Learning/tree/main/src) · [Data policy](https://github.com/hrix7/Medical-Imaging-Deep-Learning/blob/main/docs/DATA_POLICY.md)

### 02 · 3D pressure-sore tissue model
**Arizona State University · Dr. Vincent Pizziconi · Spring 2026**

**The problem:** Study how localized loading and bone-interface geometry affect the mechanical response of layered tissue.

**My contribution:** I designed a multilayer skin phantom in SolidWorks, compared spherical, steep-dome, and triangular geometries, and completed **15 FEA cases** across **1, 5, 10, 15, and 20 kPa**. I also designed channels for future embedded sensing and prepared the fabrication workflow and showcase presentation.

**Selected outcome:** For the steep-dome geometry at 20 kPa, I recorded **4.283 mm maximum displacement** and **1.211 MPa maximum von Mises stress**.

**Status:** Design and simulation work completed. Sensor integration and physical validation remain future work. The public example CSV contains one documented result and illustrative rows for exercising the analysis code; it is not the full experimental dataset.

[Explore the project](https://github.com/hrix7/3D-Pressure-Sore-Tissue-Model) · [Analysis tools](https://github.com/hrix7/3D-Pressure-Sore-Tissue-Model/tree/main/src) · [Validation plan](https://github.com/hrix7/3D-Pressure-Sore-Tissue-Model/blob/main/docs/EXPERIMENT_PLAN.md)

### 03 · Patient-specific medical design
**Operations Engineer · Steroviz Pixels Pvt. Ltd. · Dec '22 – May '24**

**The problem:** Translate CT/MRI anatomy and surgical requirements into usable models and patient-specific implant designs.

**My contribution:** I led **10+ reconstruction cases**, segmented anatomy, designed CMF and orthopedic implants, repaired STL meshes, and incorporated surgeon feedback into manufacturable designs.

**Workflow:** CT/MRI review → anatomical segmentation → mesh preparation → implant CAD → design review → additive-manufacturing preparation.

**Status:** Professional work completed during my employment. The public repository presents a sanitized workflow and mesh/DICOM utilities. Patient scans, company-owned implant files, and surgical plans are not published.

[Explore the project](https://github.com/hrix7/Patient-Specific-Medical-Design) · [Workflow](https://github.com/hrix7/Patient-Specific-Medical-Design/blob/main/docs/WORKFLOW.md) · [Geometry tools](https://github.com/hrix7/Patient-Specific-Medical-Design/tree/main/src)

### 04 · ACW Accountability Lab
**Hritika Adhikary · Independent research software project**

**The problem:** Make assessments of autonomous cyber systems transparent by connecting risk and human-control judgments to their supporting evidence.

**Project work:** A Python assessment engine with six risk dimensions, five human-control dimensions, configurable weights, evidence references and rationales. Missing evidence remains unknown and produces a score interval. Component-floor checks and weight sensitivity analysis help expose weaknesses that an average could hide.

**Outputs:** Reproducible HTML and JSON reports, structured case records, a rating guide and automated tests.

**Status:** Working research prototype. Current examples are synthetic; source-backed cases, independent ratings and research validation remain in development. Scores are not validated risk predictions or safety certifications.

[Explore the project](https://github.com/hrix7/ACW-Accountability-Lab) · [Methodology](https://github.com/hrix7/ACW-Accountability-Lab/blob/main/docs/METHODOLOGY.md) · [Roadmap](https://github.com/hrix7/ACW-Accountability-Lab/blob/main/docs/ROADMAP.md)

## Explore by field

| Field | Project | What I worked on |
| :--- | :--- | :--- |
| Medical imaging & AI | [Medical Imaging Deep Learning](https://github.com/hrix7/Medical-Imaging-Deep-Learning) | Classification, segmentation, lesion localization, GPU training |
| Biomechanics | [3D Pressure Sore Tissue Model](https://github.com/hrix7/3D-Pressure-Sore-Tissue-Model) | Multilayer CAD, geometry comparisons, 15 FEA cases |
| Human factors & ergonomics | [Tea-leaf picker ergonomic assessment](#ergonomic-assessment) | RULA, REBA, NIOSH lifting-index assessment and proposed interventions |
| Signals & wearables | [Wearable Gait and Fall-Risk System](https://github.com/hrix7/Wearable-Gait-Fall-Risk-System) | Multimodal IMU/FSR/PPG system design, gait metrics and dashboard concepts |
| Signals & wearables | [Biomedical Signal Processing](https://github.com/hrix7/Biomedical-Signal-Processing) | Physiological signal analysis |
| CAD & clinical design | [Patient-Specific Medical Design](https://github.com/hrix7/Patient-Specific-Medical-Design) | Anatomical reconstruction, implants, mesh preparation |
| Graphics & visualization | [Computer Graphics and 3D Visualization](https://github.com/hrix7/Computer-Graphics-and-3D-Visualization) | Stanford Summer Session; final rendered scene |
| Devices & translation | [Medical Device Regulatory Analysis](https://github.com/hrix7/Medical-Device-Regulatory-Analysis) | Medical-device pathways and regulatory analysis |
| IoT & sensors | [IoT Composter and Hydroponics System](https://github.com/hrix7/IoT-Composter-Hydroponics-System) | Contribution to a 10-member sensor, 3D-printing and IoT team |
| AI & automation | [AI Agent and Automation Lab](https://github.com/hrix7/AI-Agent-Automation-Lab) | AI-agent workflows, MCP and automation learning |
| AI governance & cyber accountability | [ACW Accountability Lab](https://github.com/hrix7/ACW-Accountability-Lab) | Risk profiling, human-control assessment, evidence tracking and uncertainty analysis |
| Research communication | [Conference Publications](https://github.com/hrix7/Conference-Publications) | Publication records and shareable research material |

The machine-readable repository index is maintained in [projects.yaml](projects.yaml).

### Ergonomic assessment
**Arizona State University · Dr. Thurmon Lockhart · Fall 2024**

I assessed musculoskeletal risk factors for South Asian tea-leaf pickers using RULA, REBA, and the NIOSH lifting equation, then proposed ergonomic interventions. The assessment and recommendations form the academic project; intervention effectiveness is not claimed as experimentally validated.

The portfolio includes a [CSV summary utility](scripts/ergonomic_risk_summary.py) for organizing ergonomic assessment results.

## Software projects

Project implementations and their dedicated repositories are linked below.

| Project | Implemented work | Current status | Review |
| :--- | :--- | :--- | :--- |
| [ACW Accountability Lab](https://github.com/hrix7/ACW-Accountability-Lab) | Python CLI, evidence-linked assessments, uncertainty intervals, sensitivity analysis and HTML/JSON exports | Working prototype; synthetic examples, research validation ongoing | [Source](https://github.com/hrix7/ACW-Accountability-Lab/blob/main/project.py) · [Tests](https://github.com/hrix7/ACW-Accountability-Lab/tree/main/tests) |
| [AI Job Search Crew](projects/ai-job-search-crew) | Local Python dashboard, SQLite storage, evidence matching, editable drafts, review history and application tracking | Ongoing; optional local-model testing remains pending | [Source](projects/ai-job-search-crew/app.py) · [Testing record](projects/ai-job-search-crew/TESTING.md) |
| [Embedded C Build & Memory System](https://github.com/hrix7/Embedded-Systems-Coursework) | HOST/MSP432 builds, dependency tracking, pointer-based memory operations, integer conversions and statistics | HOST tests passed; hardware execution pending | [Source](https://github.com/hrix7/Embedded-Systems-Coursework/tree/main/course1/src) · [Verification](https://github.com/hrix7/Embedded-Systems-Coursework/blob/main/course1/VERIFICATION.md) |
| [Application Desk](projects/application-desk) | Browser tracker with application records, statuses, deadlines, notes, search/filter and CSV export | Part 1 implemented; user verification and later MCP integration pending. This repository contains the overview and app link | [Project and app link](projects/application-desk/README.md) |

AI Job Search Crew uses fictional public demo data and requires human review; it does not submit applications. Software project READMEs identify AI implementation assistance. Embedded C files retain original course attribution and notices.

### Try the included code

Clone this repository and enter its directory:

```sh
git clone https://github.com/hrix7/Biomedical-Engineering-Portfolio.git
cd Biomedical-Engineering-Portfolio
```

For AI Job Search Crew:

```sh
cd projects/ai-job-search-crew
python3 app.py
# Open http://127.0.0.1:8765
```

The default workflow requires Python 3.10+ and uses the standard library. Optional local AI setup is documented in the [project README](projects/ai-job-search-crew/README.md).

For the embedded project, see the dedicated [repository and build instructions](https://github.com/hrix7/Embedded-Systems-Coursework).

## Experience

| Role | Organization | Timeline | Contribution |
| :--- | :--- | :--- | :--- |
| Biomedical Engineer | OptiBrain · Optiherence LLC | Sep '26 – present | Supporting wearable-device development through materials research, CAD design and prototyping |
| Instructional Aide · Biomaterials | Arizona State University | Jan '26 – May '26 | Graduate instruction support, grading, Canvas administration and student questions |
| Biomedical Researcher | Purcell BioPro | Jun '25 – Aug '25 | Patient-facing inhaler interface research and Figma workflow design |
| Operations Engineer | Steroviz Pixels Pvt. Ltd. | Dec '22 – May '24 | 10+ reconstruction cases, patient-specific implant design, STL preparation and surgeon collaboration |
| Biomedical Intern | Ruby General Hospital | Aug '22 – Sep '22 | Device maintenance, troubleshooting and repair support across clinical departments |

## Technical toolkit

| Area | Tools and methods |
| :--- | :--- |
| Code & data | Python, MATLAB, NumPy, pandas, OpenCV, Matplotlib, C, GNU Make |
| Medical imaging & AI | PyTorch, U-Net, ResNet, UPerNet, Faster R-CNN, Vision Transformers, 3D Slicer, ImageJ, DICOM, SLURM |
| Design & fabrication | SolidWorks, Fusion 360, PTC Creo, Meshmixer, Blender, PreForm, SLA 3D printing, Figma |
| Devices & analysis | FDA pathway analysis, SaMD, EU IVDR, FMEA, physiological signals, RULA/REBA |

## Certifications

| Certification | Provider | Project | Credential |
| :--- | :--- | :--- | :--- |
| Introduction to Embedded Systems Software and Development Environments | University of Colorado Boulder · Coursera | [Embedded C Build & Memory System](https://github.com/hrix7/Embedded-Systems-Coursework) | Certificate verification pending |

## Education

- **Arizona State University** — M.S. Biomedical Engineering · GPA 3.65/4.00
- **Stanford University** — Summer Session · Computer Graphics and Imaging
- **Adamas University** — B.Tech. Biomedical Engineering · CGPA 8.88/10

## Repository guide

- [Project catalog](projects.yaml): repository links and topic tags.
- [Catalog validator](scripts/validate_catalog.py): checks required fields and repository URL format.
- [Ergonomic summary script](scripts/ergonomic_risk_summary.py): summarizes assessment results from CSV.
- [Content checklist](docs/CONTENT_CHECKLIST.md): review steps for portfolio publication.

## Author & contact

**Hritika Adhikary** · Biomedical Engineer · Tempe, Arizona  
[LinkedIn](https://www.linkedin.com/in/hritika-adhikary-58179a1b6/) · [GitHub profile](https://github.com/hrix7)

Project settings, institutions, and professional affiliations are identified with the relevant work.

## Rights

Copyright (c) 2026 Hritika Adhikary. All rights reserved. See [LICENSE](LICENSE). Third-party course material and dependencies retain their respective licenses and attribution.
