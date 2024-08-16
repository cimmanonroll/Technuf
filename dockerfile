# Use the official Python image from the Docker Hub
FROM python:3.12

# Set the working directory
WORKDIR /technufbot

# Copy the rest of the application code into the container
COPY . .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install spacy models
RUN python -m spacy download en_core_web_sm

# Install Homebrew for pdf viewer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wkhtmltopdf \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Expose the port Streamlit runs on
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "technufbot.py"]
