
set pwd=%cd%
echo %pwd%

mkdir .\build\drivers
cd lambda_functions && (for /D %%d in (*) do (
    cd %%d
    tar -a -c -f "%pwd%\build\%%d.zip" *
    cd ..
))

cd %pwd%\ec2-scripts && tar -a -c -f "%pwd%\build\dmafv2.zip" *
cd %pwd% && copy cfn\* "%pwd%\build\"
cd %pwd% && copy cloudwatch_config\* "%pwd%\build\"
cd %pwd% && copy drivers\* "%pwd%\build\drivers"
