#!/bin/bash
ollama serve & serve=$!
sleep 30
export MODEL_NAME=llama3.2:1b
echo "Installing ${MODEL_NAME}"
ollama run ${MODEL_NAME} & llama3=$!
#wait $serve $llama3
wait $serve $llama3

