#!/bin/bash
#$ -cwd                               # run in submission directory
#$ -M cgarci32@nd.edu                 # email notifications
#$ -m abe                             
#$ -pe smp 4                          # 4 CPU cores
#$ -q gpu                             # GPU queue
#$ -l gpu=4                      # 4 GPUs
#$ -N vcc_full_gpu                    # job name
#$ -o logs/vcc_full_gpu.o$JOB_ID      # STDOUT log
#$ -e logs/vcc_full_gpu.e$JOB_ID      # STDERR log

# 1) Load and initialize Conda
module load conda
# If you’ve not already done `conda init bash`, you can source conda’s hook directly:
source /afs/crc.nd.edu/x86_64_linux/c/conda/24.7.1/etc/profile.d/conda.sh

# 2) Activate (or create/update) your env
conda activate VCCenvironment || \
  conda env create -f environment-linux.yml && conda activate VCCenvironment

# 3) Pull in any new pip-only packages
#pip install --no-cache-dir --user -r pipInstall.txt

# 4) Start Ollama’s HTTP API in the background
ollama serve &

# give the server a moment to spin up
sleep 5

# 5) Finally, run your Python script
python3 main.py

