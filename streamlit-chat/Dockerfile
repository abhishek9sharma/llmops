# Use an official Python runtime as a parent image
FROM python:3.10-slim
EXPOSE  8501
# Set the working directory in the container
WORKDIR /app

# # Copy the current directory contents into the container at /app
COPY . .

#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir uv && \
    uv pip install --system --no-cache-dir -r requirements.txt

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Run streamlit app when the container launches
RUN ls -lah
CMD ["streamlit", "run", "app.py", "--server.enableCORS=false", "--server.enableXsrfProtection=false", "--server.runOnSave=true"]
