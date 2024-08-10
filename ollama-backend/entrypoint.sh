#!/bin/bash
ollama serve & serve=$!
sleep 30
ollama run llama3 & llama3=$!

wait $serve $llama3
#wait $restapi