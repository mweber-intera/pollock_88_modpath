@echo off

rem This batch file tells all the test cases to run their individual runme.bat files to produce test case results
rem to properly run this file make sure anaconda is installed and in your system's path settings. 
rem follow the instruction included in README.md

rem in this directory with either the comand line or the anaconda prompt type <conda env create -f environment.yml> (this may take some time)
rem type <source activate modpath_qa> 
rem then in the same directory as this type <./runme.bat>

cd Test_Case_1
call runme.bat

cd ..
cd Test_Case_2
call runme.bat

cd ..
cd Test_Case_3
call runme.bat

cd ..
cd Test_Case_4
call runme.bat

cd ..
cd Test_Case_5
call runme.bat

rem # Test case 6
rem cd ..
rem cd Test_Case_6
rem call runme.bat

cd ..
python compile_results.py