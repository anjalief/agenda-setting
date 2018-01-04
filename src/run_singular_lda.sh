#!/bin/bash
module load singularity
# SET TOPIC COUNT TO 50
singularity exec /projects/tir1/singularity/ubuntu-16.04-lts_tensorflow-1.4.0_cudnn-8.0-v6.0.img ./run_english_lda_tir.sh
# singularity exec /projects/tir1/singularity/ubuntu-16.04-lts_tensorflow-1.4.0_cudnn-8.0-v6.0.img ./run_eval_lda.sh
# singularity exec /projects/tir1/singularity/ubuntu-16.04-lts_tensorflow-1.4.0_cudnn-8.0-v6.0.img ./run_dynamic.sh
# singularity exec /projects/tir1/singularity/ubuntu-16.04-lts_tensorflow-1.4.0_cudnn-8.0-v6.0.img ./run_russia_eval.sh
