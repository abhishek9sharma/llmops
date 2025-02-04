#!/bin/bash
ollama serve & serve=$!
sleep 30
#ollama run llama3 & llama3=$!
export MODEL_NAME=llama3.1:8b
echo "Installing ${MODEL_NAME}"
# ollama run ${MODEL_NAME} & codellama=$!
ollama run ${MODEL_NAME} & llama3.1:8b=$!
wait $serve $llama3
#wait $serve $codellama

#wait $restapi