@echo off
chcp 65001 > nul
echo ヒマラヤ楽天データ取得を開始します...
powershell -ExecutionPolicy Bypass -File "%~dp0fetch_himaraya.ps1"
