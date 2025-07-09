
#!/bin/bash
#$ -cwd                    #run in directory  
#$ -M cgarci32@nd.edu      # email notifications
#$ -m abe                  # mail at (a)bort, (b)egin, (e)nd
#$ -pe smp 4               # request 4 CPU cores
#$ -q gpu                  # send to the GPU queue
#$ -l gpu_card=1           # request 1 GPU
#$ -N my_python_job        # give your job a name

module load python/3.9     # load Python
module load cuda/11.8      # load CUDA (if using GPU)
export OMP_NUM_THREADS=$NSLOS

python main.py
