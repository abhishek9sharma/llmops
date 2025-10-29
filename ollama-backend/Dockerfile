FROM ollama/ollama
EXPOSE 11434
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
# Use the official Ollama Docker image as the base
# FROM ollama/ollama:latest

# # Expose the default Ollama port
# EXPOSE 11434

# # Pull the desired model when the container starts
# # This ensures the model is available upon startup
# # The sleep command is added to ensure Ollama server is fully initialized before attempting to pull
# # Adjust sleep duration if necessary based on your system's performance
# ENTRYPOINT ["/bin/bash", "-c", "sleep 5 && ollama pull llama3.2:1b && ollama serve"]