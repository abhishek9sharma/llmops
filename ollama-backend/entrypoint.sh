#!/bin/bash
ollama serve & serve=$!
sleep 30
#ollama run llama3 & llama3=$!
ollama run codellama:7b & codellama=$!
#wait $serve $llama3
wait $serve $codellama

#wait $restapi