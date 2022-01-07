#!/bin/bash
pwd=$PWD
echo $pwd
mkdir -p "$pwd/build"
mkdir -p "$pwd/build/drivers"
cd lambda_functions
for f in *; do
    if [ -d "$f" ]; then
        # $f is a directory
        echo $f
        cd $f
        zip -r "$pwd/build/$f.zip" *
        cd ..
    fi
done
cd $pwd
cd ec2-scripts
zip -r "$pwd/build/dmafv2.zip" * -x oracle_performance.sql
cd $pwd
cp cfn/* "$pwd/build/."
cd $pwd
cp cloudwatch_config/* "$pwd/build/."
cd $pwd
cp drivers/* "$pwd/build/drivers/."