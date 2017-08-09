#!/bin/sh

if [ -z "$COMPUTE_DATA_DIR" ]; then
  COMPUTE_DATA_DIR=/opt/DeepSpeech/data
fi

python -u DeepSpeech.py \
  --train_files "${COMPUTE_DATA_DIR}/librivox-train-clean-100.csv" \
  --dev_files "${COMPUTE_DATA_DIR}/librivox-dev-clean.csv" \
  --test_files "${COMPUTE_DATA_DIR}/librivox-test-clean.csv" \
  --train_batch_size 16 \
  --dev_batch_size 8 \
  --test_batch_size 8 \
  --epoch=50 \
  --learning_rate 0.0001 \
  --display_step 10 \
  --validation_step 10 \
  --dropout_rate 0.30 \
  --default_stddev 0.046875 \
  --checkpoint_step 1 \
  --checkpoint_dir "${COMPUTE_KEEP_DIR}" \
  --wer_log_pattern "GLOBAL LOG: logwer('${COMPUTE_ID}', '%s', '%s', %f)"\
  "$@"
