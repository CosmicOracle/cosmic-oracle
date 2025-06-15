# Clean script for Windows
Write-Host "Cleaning up..."

# Remove node_modules if it exists
if (Test-Path "node_modules") {
    Write-Host "Removing node_modules..."
    Remove-Item -Recurse -Force node_modules
}

# Remove package-lock.json if it exists
if (Test-Path "package-lock.json") {
    Write-Host "Removing package-lock.json..."
    Remove-Item -Force package-lock.json
}

# Install dependencies
Write-Host "Installing dependencies..."
npm install

# Install TypeScript types
Write-Host "Installing TypeScript types..."
npm install --save-dev @types/react-router-dom

Write-Host "Clean and install complete!"
