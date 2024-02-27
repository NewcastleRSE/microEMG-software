% test MatLab functions, to be compared to results given from "test_python_functions.py"
clear
clc

format long

% length of vector to test
l = 70;
% test vector
vec = 1:l;

% convert ot column vector
vec= vec(:);

% offset
k = 1;

disp("out1:");
out1 = runningTEO(vec, k);
disp(out1)

%%%%%%%%%%%%%%%%%%%%%%
ks = [2 3 5];


[runTEO, tmp] = MTEO(vec, ks);

disp("out2:");
disp(runTEO);

