# Setup and reproducibility

This repository was developed on Windows with Python 3.12.10. Dependencies are pinned in the root `requirements.txt`; use those versions rather than relying on an older dependency list.

## Windows CMD

```cmd
git clone https://github.com/AvivRomHoresh/Secure-AI-SOC.git
cd Secure-AI-SOC
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pip check
python -m streamlit run demo/app.py
```

Open `http://localhost:8501` for the **offline experiment replay**. The dashboard uses existing experiment records, including fallback files under `demo/fallback/`; it does not need a live LLM or detector retraining.

## Live LLM requirements

To run LLM inference scripts rather than replay results, install Ollama separately and pull the locally evaluated model:

```cmd
ollama pull llama3.2:3b
```

The recorded evaluation used temperature 0, seed 42, and a context window of 8192. Consult the frozen experiment protocols and configuration before attempting new runs. New executions are **not** part of the original 63-run official experiment.

## Reproducibility notes

- Synthetic results do not imply production performance.
- The official experiment manifest is at `experiments/prompt_injection/PHASE11_EXPERIMENT_MANIFEST.json`.
- The offline dashboard's fallback manifest is a local copy; its authenticity is not independently established by the dashboard.
- The demo verifies referenced run-log hashes against its selected manifest; it is not a full independent authenticity audit.
- Interactive decisions written under `demo/decisions/` are separate from official recorded human decisions.
- Trained model files or data excluded by `.gitignore` may require regeneration; consult the scripts and model/dataset documentation before rerunning model evaluation.
