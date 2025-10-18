#!/bin/bash
ollama serve & serve=$!
sleep 30
export MODEL_NAME=llama3.1:8b
echo "Installing ${MODEL_NAME}"
ollama run ${MODEL_NAME} & llama3.1:8b=$!
wait $serve $llama3
