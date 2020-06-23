#!/bin/bash

#SBATCH -N 1-1
#SBATCH --cpus-per-task=---cpus---
#SBATCH --mem-per-cpu=---memperCPU---
#SBATCH --mail-type=ALL
#SBATCH --mail-user=---email---
#SBATCH --error=---errpath---


TEMPLATEFLOW_HOST_HOME=---tflow_path---

export SINGULARITYENV_TEMPLATEFLOW_HOME='/templateflow'

singularity run --cleanenv ---mounts--- ---imloc--- ---data_base--- ---outputpath--- participant --participant-label ---pid--- -w ---wpath--- --output-spaces ---output_spaces--- --mem_mb ---mem_mb--- --fs-subjects-dir ---fsdir--- --omp-nthreads ---ot--- --nthreads ---nt--- --fs-license-file ---fsli--- ---optionals---


