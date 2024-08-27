# Use the official Ubuntu base image
FROM ubuntu:latest

# Update the package list and install necessary dependencies
RUN apt-get update
RUN apt-get install -y python3 python3-pip

COPY . .

RUN pip3 install --break-system-packages -r requirements.txt

# Define the command to run the application
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]