@echo off
cd "C:\Users\Administrator\.openclaw\workspace\projects\iraq-website-business\generated_sites\deploy_temp"
(
echo clawadam828@gmail.com
echo P@ssw0rd@123.com.
) | surge login
surge . dca-dental-clinic.surge.sh
pause
