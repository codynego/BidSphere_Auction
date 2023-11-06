#!/bin/bash

# Backend commands

echo "Running Migrations..."
python backend/manage.py migrate


echo "Collecting Static Files..."
python backend/manage.py collectstatic --noinput


echo "running cron jobs..."
python backend/manage.py runcrons


echo "Starting Server..."
python backend/manage.py runserver

# Frontend commands

echo "Installing Frontend Dependencies..."
cd frontend
npm install
npm run build
npm run start