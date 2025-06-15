#!/bin/bash

# Setup and test script for cosmic-oracle-frontend

echo "Installing npm dependencies..."
npm install

echo "Running lint..."
npm run lint

echo "Running type-check..."
npm run type-check

echo "Starting frontend development server..."
npm start
