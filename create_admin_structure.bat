@echo off
cd /d C:\TruongVanKhai\Project\uni_bot\frontend\src

echo Creating admin directory structure...

if not exist "app\admin" mkdir "app\admin"
if not exist "app\admin\dashboard" mkdir "app\admin\dashboard"
if not exist "app\admin\chat-history" mkdir "app\admin\chat-history"
if not exist "app\admin\documents" mkdir "app\admin\documents"
if not exist "components\admin" mkdir "components\admin"

echo Directories created successfully!
echo.
dir /b app\admin
echo.
echo Done!
