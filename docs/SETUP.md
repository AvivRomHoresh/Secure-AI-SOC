# Development Environment Setup

## Project
Secure & Explainable AI-Powered SOC

## Environment
- Operating System: Windows
- Python: 3.12.10
- Virtual Environment: Python venv

## Installation

### 1. Clone the Repository

```cmd
git clone https://github.com/AvivRomHoresh/Secure-AI-SOC.git
cd Secure-AI-SOC
```

### 2. Create a Virtual Environment

```cmd
python -m venv .venv
```

### 3. Activate the Environment

```cmd
.venv\Scripts\activate
```

### 4. Install Dependencies

```cmd
python -m pip install -r requirements.txt
```

### 5. Verify Installation

```cmd
python -m pip check
```

## Initial Dependencies

- NumPy: 2.5.3
- Pandas: 3.0.6
- Scikit-learn: 1.9.1

Additional dependencies will be documented as the project develops.

## Notes

- The virtual environment is excluded from Git.
- Dependencies are defined in `requirements.txt`.
- Trained models and large datasets may require separate setup instructions.
- NVIDIA Morpheus is optional and is not required for the core project.
