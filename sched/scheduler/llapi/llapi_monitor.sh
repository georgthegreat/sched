#!/bin/sh

# Expects LoadLeveler jobId in $1
JOB_ID=$1
# Expects Named pipe path in $2
FIFO_STREAM=$2
echo $JOB_ID >> $FIFO_STREAM

