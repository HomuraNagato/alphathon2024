
# unix script to orchestrate train/test data creation, fine-tuning, and testing

# Check if arguments are passed
if [ "$#" -eq 0 ]; then
  echo "Error: No arguments provided"
  exit 1
fi

CLIENT=sp500_10k
FNAME=001
STEP=$1
V=v01
REL_DIR=./mooncake/llm/
CONFIG=$REL_DIR/configs/config_$CLIENT.yaml
DATA=mooncake/data/10ks/10ks_truths.csv

if [ $STEP = "0" ]; then
    python $REL_DIR/utils/config_editor.py \
           --config $CONFIG \
           --client $CLIENT \
           --model_key_base model_key_v000 \
           --model_key model_v$FNAME
fi

#           --sample 200 \
if [ $STEP = "1" ]; then
    python $REL_DIR/models/train/train_data_preparatory.py \
           --client $CLIENT \
           --data_path $DATA \
           --train_path mooncake/data/$CLIENT/$V/train_$FNAME.csv \
           --test_path mooncake/data/$CLIENT/$V/test_$FNAME.csv \
           --config $CONFIG \
           --split 0.5 \
           --threshold 20 \
           --unique 
fi

if [ $STEP = "2" ]; then
    python $REL_DIR/models/train/train_message_preparatory.py \
           --client $CLIENT \
           --config $CONFIG \
           --train_path mooncake/data/$CLIENT/$V/train_$FNAME.csv \
           --message_path mooncake/data/$CLIENT/$V/m$FNAME.jsonl
fi

if [ $STEP = "3" ]; then
    python $REL_DIR/models/train/finetune_model.py \
           --message_path mooncake/data/$CLIENT/$V/m$FNAME.jsonl \
           --model gpt-4o-mini-2024-07-18
fi

if [ $STEP = "4" ]; then
    python $REL_DIR/utils/config_editor.py \
           --config $CONFIG \
           --data_path data/$CLIENT/$V/$DATA \
           --model ft:gpt-4o-mini-2024-07-18:personal::A9FWA9lp \
           --model_key model_v$FNAME \
           --top_p 1
fi

if [ $STEP = "5" ]; then
    python $REL_DIR/models/test/test_model_output.py \
           --config $CONFIG \
           --model_key model_v$FNAME \
           --test_path mooncake/data/$CLIENT/$V/test_$FNAME.csv \
           --test_response_path mooncake/data/$CLIENT/$V/o$FNAME.csv
fi

if [ $STEP = "6" ]; then
    python $REL_DIR/models/test/test_model_statistics.py \
           --test_response_path mooncake/data/$CLIENT/$V/o$FNAME.csv \
           --statistic_path mooncake/data/$CLIENT/$V/s$FNAME.csv
fi
