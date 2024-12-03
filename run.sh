#!/bin/bash

# Start the Python backend
cd backend || exit
python app.py &

# Start the Angular frontend
cd ../frontend/ATAM-RAG-Tool || exit
npx -p @angular/cli ng serve &

# Wait for both background processes to complete
wait

