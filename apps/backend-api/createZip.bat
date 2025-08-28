@echo off
"C:\Program Files\7-Zip\7z.exe" a -tzip "deploy\backend_endpoint.zip" "core" "endpoint" "requirements.txt" "app.py" -x!".conda" -x!".vscode" -x!".idea" -x!"conf\data.db" -x!"deploy" -x!"test" -x!".gitignore" -x!"createZip.bat" -xr!"__pycache__" -aoa
pause
