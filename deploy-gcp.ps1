name: Deploy to Google Cloud

on:
  push:
    branches:
      - main
  workflow_dispatch:

env:
  GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  GCP_REGION: ${{ secrets.GCP_REGION }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: 'read'
      id-token: 'write'
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - id: 'auth'
        name: 'Authenticate to Google Cloud'
        uses: 'google-github-actions/auth@v2'
        with:
          workload_identity_provider: '${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}'
          service_account: '${{ secrets.GCP_SA_EMAIL }}'
      
      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2
        with:
          project_id: ${{ env.GCP_PROJECT_ID }}
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          cache: 'pip'
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: './cosmic-oracle-frontend/package-lock.json'
      
      - name: Deploy Backend
        working-directory: ./cosmic-oracle-backend
        run: |
          pip install -r requirements.txt
          pip install gunicorn
          gcloud app deploy app.yaml --quiet
      
      - name: Build Frontend
        working-directory: ./cosmic-oracle-frontend
        run: |
          npm ci
          npm run build
      
      - name: Create Frontend App Engine Config
        working-directory: ./cosmic-oracle-frontend
        run: |
          cat > app.yaml << 'EOL'
          runtime: nodejs18
          service: cosmic-oracle-frontend
          
          handlers:
            - url: /static
              static_dir: build/static
              secure: always
              
            - url: /(.*\.(json|ico|js|css|png|jpg|jpeg|gif|svg|txt|html|xml|woff|woff2|ttf|eot))$
              static_files: build/\1
              upload: build/.*\.(json|ico|js|css|png|jpg|jpeg|gif|svg|txt|html|xml|woff|woff2|ttf|eot)$
              secure: always
              
            - url: /.*
              static_files: build/index.html
              upload: build/index.html
              secure: always
          
          env_variables:
            NODE_ENV: "production"
            REACT_APP_API_URL: "https://cosmic-oracle-backend-dot-${{ env.GCP_PROJECT_ID }}.appspot.com"
          EOL
      
      - name: Deploy Frontend
        working-directory: ./cosmic-oracle-frontend
        run: |
          gcloud app deploy app.yaml --quiet
      
      - name: Display deployment URLs
        run: |
          echo "Backend deployed to: https://cosmic-oracle-backend-dot-${{ env.GCP_PROJECT_ID }}.appspot.com"
          echo "Frontend deployed to: https://cosmic-oracle-frontend-dot-${{ env.GCP_PROJECT_ID }}.appspot.com"