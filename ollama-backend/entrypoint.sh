#!/bin/bash
ollama serve & serve=$!
sleep 30
#ollama run llama3 & llama3=$!
export MODEL_NAME=codellama:7b
echo "Installing ${MODEL_NAME}"
ollama run ${MODEL_NAME} & codellama=$!
#wait $serve $llama3
wait $serve $codellama

#wait $restapi