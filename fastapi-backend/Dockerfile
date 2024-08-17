# Use an official Python runtime as a parent image
FROM python:3.10-slim
EXPOSE 8001
# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
#COPY requirements.txt requirements.txt

# Install any needed packages specified in requirements.txt
#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install fastapi uvicorn sentence_transformers langchain==0.1.12 openai==1.7.2  langchain-openai==0.0.2 langchain==0.1.12 openai==1.7.2 \
    langchainhub==0.1.14 python-multipart chromadb==0.4.22 pandas

#RUN pip install langchain-community<0.1 
   
# Make port 8001 available to the world outside this container
EXPOSE 8001

# Run uvicorn to serve the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]