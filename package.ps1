$pwd = $PWD.Path
echo $pwd
New-Item .\build\drivers -ItemType Directory
Get-ChildItem -Path  $pwd\lambda_functions |
    Foreach-Object {
        Compress-Archive -Path $pwd\lambda_functions\$_\*.* -DestinationPath $pwd\build\$_.zip
    }
Compress-Archive -Path $pwd\ec2-scripts\* -DestinationPath $pwd\build\dmafv2.zip
Copy-Item -Path $pwd\cfn\* -Destination $pwd\build\
Copy-Item -Path $pwd\cloudwatch_config\* -Destination $pwd\build\
Copy-Item -Path $pwd\drivers\* -Destination $pwd\build\drivers
