#!/bin/bash
#PBS -N checkGit
#PBS -l walltime=00:05:00,nodes=1:ppn=1
#PBS -j oe

echo "=== Running on $(hostname) ==="
ls -ld $HOME/CSA-2025-Dataset/.git
