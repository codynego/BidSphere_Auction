#!/bin/bash

# Backend commands

echo "Running Migrations..."
python backend/manage.py migrate

echo "Starting Server..."
python backend/manage.py runserver &

# Frontend commands

echo "Installing Frontend Dependencies..."
cd frontend
npm install

echo "Starting Frontend Server..."
npm run dev
