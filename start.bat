@echo off
chcp 65001 >nul
echo ================================================
echo    IRAQ WEBSITE BUSINESS - لوحة التحكم
echo ================================================
echo.
echo [1] فتح الداشبورد
echo [2] إضافة زبون
echo [3] معالجة زبون (توليد + نشر + إرسال)
echo [4] عرض الزبائن
echo [5] خروج
echo.
set /p choice="اختر رقم: "

if "%choice%"=="1" goto dashboard
if "%choice%"=="2" goto add
if "%choice%"=="3" goto process
if "%choice%"=="4" goto list
if "%choice%"=="5" goto end

:dashboard
python main.py dashboard
pause
goto end

:add
set /p name="اسم العمل: "
set /p phone="الهاتف: "
set /p category="الفئة (clinic/restaurant/salon/shop/other): "
python main.py add "%name%" "%phone%" "%category%"
pause
goto end

:process
set /p id="رقم الزبون: "
python main.py process %id%
pause
goto end

:list
python -c "import json; db=json.load(open('database.json', encoding='utf-8')); [print(f'{b[\"id\"]}. {b[\"name\"]} - {b[\"phone\"]} ({b[\"status\"]})') for b in db['businesses']]"
pause
goto end

:end
