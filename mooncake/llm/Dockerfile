
FROM python:3

# Create directory
WORKDIR /home

# copy static files
COPY llm/requirements.txt .

# Install needed packages
RUN pip install --no-cache-dir -r requirements.txt

# files passed by reference via docker-compose
#COPY . .

# dockenter ft-cls to run programs
