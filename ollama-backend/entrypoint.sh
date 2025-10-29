#!/bin/bash
ollama serve & serve=$!
export MODEL_NAME=llama3.2:1b
echo "Installing ${MODEL_NAME}"
ollama run ${MODEL_NAME} & model_pid=$!
wait $serve_pid $model_pid
