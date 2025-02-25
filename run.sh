#!/bin/bash

VENV_PATH=$(find "$PWD" -type d -name ' bash-venv')
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


streamlit run main.py