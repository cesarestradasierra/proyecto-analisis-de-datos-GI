@echo off
echo ==========================================
echo   EJECUTANDO PIPELINE DE INVENTARIO...
echo ==========================================

"C:\Users\cesar\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe" src/01_ingesta_apis.py

"C:\Users\cesar\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe" src/02_transformacion.py

echo ==========================================
echo   PROCESO TERMINADO CON EXITO
echo ==========================================
pause