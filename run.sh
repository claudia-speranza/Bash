#!/bin/bash

# --- Virtual Env ---
VENV_PATH=$(find "$PWD" -type d -name 'bash-venv')
FOUND_KERNEL=$(find "$PWD" -type d -name 'bash-venv' | wc -l)

if [ "$FOUND_KERNEL" -eq 0 ]
then
  echo "Virtual environment not present in this machine, creating it.."
  python3 -m venv ./bash-venv
  source ./bash-venv/bin/activate
  echo "Installing all requirements from pip..."
  pip install --quiet --upgrade pip
  pip install --quiet -r requirements.txt
else
  echo "Virtual environment found in ${VENV_PATH}, updating it.."
  source "${VENV_PATH}"/bin/activate
  echo "Updating all requirements from pip..."
  #pip install --quiet -r requirements.txt

fi


# --- Virtual Env ---

# Check if container named timescaledb exists
if sudo docker ps -a --format '{{.Names}}' | grep -q "^postgres-db$"; then
    # Container exists, check if it's running
    if sudo docker ps --format '{{.Names}}' | grep -q "^postgres-db$"; then
        echo "Container 'postgres-db' is already running."
    else
        # Container exists but is not running, start it
        echo "Starting existing 'postgres-db' container..."
        sudo docker start postgres-db
    fi
else
    # Container doesn't exist, create and run it
    echo "Creating and starting 'timescaledb' container..."
    sudo docker run -d \
        --name postgres-db \
        -e POSTGRES_USER=$POSTGRES_USER \
        -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
        -e POSTGRES_DB=$POSTGRES_DB \
        -p ${POSTGRES_PORT}:5432 \
        postgres
fi
streamlit run main.py