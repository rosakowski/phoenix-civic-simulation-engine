# Getting Started on Mac (Alternative Commands)

If `pip` and `python` commands aren't found, try these alternatives:

## Option 1: Use Python 3 explicitly
```bash
# Check Python version
python3 --version

# Install dependencies
python3 -m pip install -r requirements.txt

# Run the API server
python3 pcse/api.py
```

## Option 2: Use pyenv (if installed)
```bash
# Install via pyenv
pyenv install 3.11.0  # or latest
pyenv local 3.11.0
pip install -r requirements.txt
python pcse/api.py
```

## Option 3: Use Homebrew Python
```bash
# Install via Homebrew
brew install python@3.11
/opt/homebrew/bin/python3 -m pip install -r requirements.txt
/opt/homebrew/bin/python3 pcse/api.py
```

## Option 4: Use Conda/Miniconda
```bash
# Create conda environment
conda create -n phoenix python=3.11
conda activate phoenix
pip install -r requirements.txt
python pcse/api.py
```

## Testing Your Installation

```bash
# Check Python
which python3
python3 --version

# Check pip
python3 -m pip --version
```

## Running the System

Once Python is working:
```bash
# Navigate to project directory
cd phoenix-civic-simulation-engine

# Install dependencies
python3 -m pip install -r requirements.txt

# Start the server
python3 pcse/api.py

# Open dashboard
open http://localhost:8000/dashboard
```

## What You Should See

1. Server startup messages
2. "Phoenix Civic Simulation Engine API starting..."
3. "Dashboard available at: http://localhost:8000/dashboard"
4. Interactive map with heat vulnerability zones
5. Intervention toggles you can click

---

**Claude Code Integration:**

Yes! Connecting Claude Code to GitHub would be fantastic. It could:
- Help implement new features
- Write tests
- Refactor code
- Contribute to documentation
- Suggest improvements

This would be a great example of human-AI-AI collaboration! Let me know what you'd like to set up.# Add this to your .bashrc or .zshrc
export PATH="/usr/local/bin:$PATH"
