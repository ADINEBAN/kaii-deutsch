@echo off
echo ============================================================
echo   Pushing code to GitHub ADINEBAN/kaii-deutsch
echo ============================================================
echo.
git push -u kaii main
echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Code pushed to GitHub successfully!
) else (
    echo [NOTE] If prompted, please choose 'Sign in with your browser'.
)
echo.
pause
