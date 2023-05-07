
# Autoprune

## Usage

### Generate Candidates

./synth --check --reinfer-rhs --solver-timeout=0 --souper-debug-level=3 --souper-enumerative-synthesis-ignore-cost --souper-enumerative-synthesis-max-instructions=1 --souper-check-all-guesses dataset.opt

### Extract the features

python extract.py

### Train/Test

python classify.py