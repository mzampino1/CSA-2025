#!/bin/bash
#$ -N codellama_ft
#$ -q gpu
#$ -pe smp 4
#$ -l gpu=4
#$ -cwd
#$ -o logs/$JOB_NAME.o$JOB_ID
#$ -e logs/$JOB_NAME.e$JOB_ID
#$ -l h_rt=12:00:00


module load cuda/12.1
module load python/3.12.11
module load conda

source activate VCCenvironment
cd $HOME/CSA-2025

# Ensure user‐installed bin folder is on PATH (for any local installs)
export PATH="$HOME/.local/bin:$PATH"
export PYTHONPATH=$PYTHONPATH:/users/cgarci32/CSA-2025



# Force torchrun to use IPv4 rendezvous
export MASTER_ADDR=127.0.0.1
export MASTER_PORT=29500

# Launch using the correct path to your script
torchrun \
  --nproc_per_node=4 \
  --master_addr=$MASTER_ADDR \
  --master_port=$MASTER_PORT \
  Trainers/train_injector.py
