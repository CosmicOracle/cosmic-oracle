@echo off
echo Cleaning up...

:: Remove node_modules if it exists
if exist node_modules (
    echo Removing node_modules...
    rmdir /s /q node_modules
)

:: Remove package-lock.json if it exists
if exist package-lock.json (
    echo Removing package-lock.json...
    del /f package-lock.json
)

echo Installing dependencies...
call npm install

echo Installing TypeScript types...
call npm install --save-dev @types/react-router-dom

echo Clean and install complete!
pause
