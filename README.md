# Hi, I'm Vridhi 👋

I’m an Electrical & Electronic Engineering undergraduate at NTU with interests spanning AI, machine learning, data analytics, software engineering, embedded systems and biomedical applications.

I enjoy turning data and ideas into practical solutions from explainable health analytics and intelligent applications to sensor-based systems, while exploring how software, hardware and AI can work together to solve real-world problems.

## Featured projects

### [Mosaic — catalogue-grounded AI shopping search](https://github.com/VT2305/VT2305/tree/main/projects/mosaic)

A working natural-language shopping search prototype with structured intent extraction, hard-constraint filtering, interpretable product ranking and catalogue-grounded explanations. Includes a browser demo, FastAPI backend, a fictional 48-product catalogue and a reproducible evaluation suite.

**Engineering focus:** separating non-negotiable product constraints from soft preferences, then making recommendation scores explainable.  
**Verified locally:** 32 automated tests passed; 40 synthetic benchmark queries with no hard-constraint violations in returned results. This is a prototype, not a production search engine.

`Python` · `FastAPI` · `Pydantic` · `Search & Ranking` · `Evaluation`

### [HeatShift - decision support for heat-aware work planning](https://github.com/VT2305/heatshift-agent)

A FastAPI application combining versioned rules, OR-Tools CP-SAT scheduling, validation, supervisor approval and an audit trail. Optional Bedrock/AgentCore integrations sit alongside a local demo.

**Engineering focus:** separating optimisation and validation from LLM explanations.  
**Verified locally:** 12 tests passed. AWS deployment and operational validation remain separate work.

`Python` · `FastAPI` · `OR-Tools` · `SQLite` · `Agentic AI`

### [SoCPerfSim - C++ memory-system simulator](https://github.com/VT2305/socperfsim)

A trace-driven L1/L2/DRAM simulator with configurable caches, replacement policies, dirty evictions and JSON metrics. Python tools generate synthetic workloads and automate configuration sweeps.

**Engineering focus:** understanding the cost of data movement.  
**Verified locally:** Release build, cache tests, demo trace and a 36-configuration sweep completed. The model is educational, not hardware-calibrated.

`C++17` · `CMake` · `Python` · `Performance modelling`

### [Heart Age Engine - explainable ML exploration](https://github.com/VT2305/heart-age-engine)

A public refactor of a four-person NTU project exploring cardiovascular data. My coursework contributions focused on LOF anomaly detection, label/model disagreement analysis and an interactive simulator.

**Engineering focus:** reusable preprocessing, a chronological-age leakage guardrail, SHAP explanations and explicit model limitations.  
**Verified locally:** 4 unit tests and lint checks passed. Full-dataset results require the separately supplied dataset.

`Python` · `scikit-learn` · `SHAP` · `Streamlit`

### [KinetiQ Edge - movement-sensing prototype](https://github.com/VT2305/kinetiq-edge)

An early prototype combining a React dashboard, BMI270 serial-acquisition scaffold and a subject-grouped random-forest baseline.

**Engineering focus:** connecting embedded sensing with measurable ML evaluation.  
**Verified locally:** dashboard production build and synthetic baseline run. The dashboard uses simulated values; on-device ML and BLE integration remain planned.

`React` · `Python` · `Arduino C++` · `nRF52840`

## Tools and interests

- **Programming:** Python, C/C++, SQL, MATLAB
- **Software and data:** FastAPI, Git, pytest, NumPy, pandas
- **ML:** scikit-learn, SHAP, model evaluation and explainability
- **Exploring:** embedded AI, computer architecture, computer vision and robotics

[Connect on LinkedIn](https://www.linkedin.com/in/vridhi-talwar-5a1312373)
