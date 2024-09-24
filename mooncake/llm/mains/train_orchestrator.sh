
# unix script to orchestrate train/test data creation, fine-tuning, and testing

# TODO, move config to V; remove variable FNAME?

# Check if arguments are passed
if [ "$#" -eq 0 ]; then
  echo "Error: No arguments provided"
  exit 1
fi

CLIENT=sp500_10k_demo
FNAME=001
STEP=$1
V=v01
#REL_DIR=./mooncake # set in docker-compose
LLM_DIR=./mooncake/llm
CONFIG=$LLM_DIR/configs/config_$CLIENT.yaml
FNAME_10ks=mooncake/data/10ks/form-10-K-all.csv
FNAME_SP500=mooncake/data/sp500s/sp500cik.csv
FNAME_MERGED=mooncake/data/merged/10ks_truths.csv
QUANTCONNECT_DATA_DIR=./data/10ks

if [ $STEP = "0" ]; then
    python $LLM_DIR/utils/config_editor.py \
           --config $CONFIG \
           --client $CLIENT \
           --model_key_base model_key_v000 \
           --model_key model_v$FNAME
fi

#           --fname_out =     "./mooncake/data/sp500list/sp500_truths.csv" \
#           --out_dir "./data/sp500_symbols/" \
if [ $STEP = "1" ]; then
    python $LLM_DIR/../utils/prep_sp500_10ks_data.py \
           --fname_10ks $FNAME_10ks \
           --fname_sp500 $FNAME_SP500 \
           --fname_out $FNAME_MERGED \
           --out_dir $QUANTCONNECT_DATA_DIR \
           --how "left" \
           --window_size 10 
fi

if [ $STEP = "2" ]; then
    python $LLM_DIR/models/train/train_data_preparatory.py \
           --client $CLIENT \
           --data_path $FNAME_MERGED \
           --train_path mooncake/data/$CLIENT/$V/train_$FNAME.csv \
           --test_path mooncake/data/$CLIENT/$V/test_$FNAME.csv \
           --config $CONFIG \
           --sep "|" \
           --sample 100 \
           --split 0.5 \
           --threshold 20 \
           --unique 
fi

if [ $STEP = "3" ]; then
    python $LLM_DIR/models/train/train_message_preparatory.py \
           --client $CLIENT \
           --config $CONFIG \
           --train_path mooncake/data/$CLIENT/$V/train_$FNAME.csv \
           --message_path mooncake/data/$CLIENT/$V/m$FNAME.jsonl
fi

if [ $STEP = "4" ]; then
    python $LLM_DIR/models/train/finetune_model.py \
           --message_path mooncake/data/$CLIENT/$V/m$FNAME.jsonl \
           --model gpt-4o-mini-2024-07-18
fi

if [ $STEP = "5" ]; then
    python $LLM_DIR/utils/config_editor.py \
           --config $CONFIG \
           --data_path data/$CLIENT/$V/$FNAME_MERGED \
           --model ft:gpt-4o-mini-2024-07-18:personal::AAmmUnen \
           --model_key model_v$FNAME \
           --top_p 1
fi

if [ $STEP = "6" ]; then
    python $LLM_DIR/models/test/test_model_output.py \
           --config $CONFIG \
           --model_key model_v$FNAME \
           --sample 10 \
           --test_path mooncake/data/$CLIENT/$V/test_$FNAME.csv \
           --test_response_path mooncake/data/$CLIENT/$V/o$FNAME.csv
fi

if [ $STEP = "7" ]; then
    python $LLM_DIR/models/test/test_model_statistics.py \
           --test_response_path mooncake/data/$CLIENT/$V/o$FNAME.csv \
           --statistic_path mooncake/data/$CLIENT/$V/s$FNAME.csv
fi
