# dmafv2

To create the package run the below command

```
./package.sh
```
output:
```
$ ./package.sh
asyncmodifycsvfiles
updating: lambda_function.py (deflated 79%)
athenacreation
updating: athenaTablesViews.sql (deflated 83%)
updating: cfnresponse.py (deflated 56%)
updating: lambda_function.py (deflated 67%)
updating: rds_instance_type.csv (deflated 69%)
updating: url.csv (deflated 64%)
updating: wqf_2nd_values.csv (deflated 29%)
updating: wqf_estimate_default.csv (deflated 77%)
modifycsvfiles
updating: lambda_function.py (deflated 76%)
sqspoll
updating: lambda_function.py (deflated 57%)
timecalculation
updating: lambda_function.py (deflated 81%)
updating: awr.py (deflated 72%)
updating: dmafuser_grants.sql (deflated 86%)
updating: get_mssql_performance.sql (deflated 60%)
updating: input.csv (deflated 17%)
updating: run_sct.py (deflated 69%)
updating: staticfiles/ (stored 0%)
updating: staticfiles/dmafDataStructures/ (stored 0%)
updating: staticfiles/dmafDataStructures/ComplexityWeightage.csv (stored 0%)
updating: staticfiles/dmafDataStructures/tables2csvfiles.sql (deflated 83%)
updating: staticfiles/dmafDataStructures/actcoderanges.csv (deflated 53%)
updating: staticfiles/dmafDataStructures/lambdadatat.sql (deflated 47%)
updating: staticfiles/dmafDataStructures/rds_instance_type.csv (deflated 61%)
updating: staticfiles/dmafDataStructures/lambdadata2.sql (deflated 43%)
updating: staticfiles/dmafDataStructures/sctactioncodes.csv (deflated 83%)
updating: staticfiles/dmafDataStructures/wqf_estimate_default.csv (deflated 77%)

```
Required deployment files will packaged in build dir:
```
$ ls
README.md		acat_report		cfn			ec2-scripts		mpi4py-3.0.3		prerequisites
acat-output.json	build			cfnnag.log		lambda_functions	package.sh
$ ls build/
asyncmodifycsvfiles.zip			dmafv2.zip				sqspoll.zip
athenacreation.zip			modifycsvfiles.zip			timecalculation.zip
dmaf-dk-4.yml				quicksight-ProServe-Ohio.yml
dmaf-dk.yml				quicksight-fast_PS_Oregon-DEV.yml
``` 
upload all the files in the build dir to s3 bucket to create the stack.
