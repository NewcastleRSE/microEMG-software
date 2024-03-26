tmp<-c(1.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00,
 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00,
 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00,
 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00,
 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00,
 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00,
 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00,
 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00,
 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00,
 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.000e+00, 4.761e+03, 4.900e+03)
 
 var(tmp)
 
 n<-length(tmp)
 var(tmp)*(n-1)/n
 
 
 x<-seq(1, 10, 0.1)

for(i in 1:4)
{ 
 y<-i*sin(x)+cos(i*1.1234*x) + 0.2*rnorm(length(x))
 
 length(x)
 
 dev.new()
 
 plot(x, y, type="l")
 
 print(y)
} 

fpy0<-read.csv('C:\\Users\\richa\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\features0_python_pre_gen_titles.csv', header = FALSE, nrows=80000)

fmat0<-read.csv('C:\\Users\\richa\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\features0_matlab_pre_gen_titles.csv', header = FALSE, nrows=80000)

fpy<-read.csv('C:\\Users\\richa\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\features_python_pre_gen_titles.csv', header = FALSE)#, nrows=80000)

fmat<-read.csv('C:\\Users\\richa\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\features_matlab_pre_gen_titles.csv', header = FALSE)#, nrows=80000)

fpy<-as.matrix(fpy)
fpy0<-as.matrix(fpy0)
fmat<-as.matrix(fmat)
fmat0<-as.matrix(fmat0)


#d<-fpy-fmat

#nfpy<-fpy
#nfpy[!(fmat == 10 & fpy != 10)]<-0


sum((is.nan(fmat) & !is.nan(fpy)))

sum((is.nan(fmat) & !is.nan(fpy)))

sum((is.nan(fmat0) & !is.nan(fpy0)))

sum((!is.nan(fmat) & is.nan(fpy)))

sum((!is.nan(fmat0) & is.nan(fpy0)))

diffRows<-which(rowSums(is.nan(fmat) & !is.nan(fpy)) != 0)

fpy[diffRows,]

fmat[diffRows,]

diffRows

#sum((is.nan(fpy) & !is.nan(fpy)))

#fpy[is.nan(fpy)]<-10

#fmat<-as.matrix(fmat)
#fmat[is.nan(fmat)]<-10

dif<-(fpy!=fmat)

sum(dif)

diffRows2<-which(rowSums(fmat != fpy) != 0)

fpy[diffRows2,]

fmat[diffRows2,]

diffRows2

#check titles
tmat<-read.csv('C:\\Users\\richa\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\matlab_the_titles.csv', header = FALSE)[,1]

tpy<-read.csv('C:\\Users\\richa\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\python_the_titles.csv', header = FALSE)[,1]

checked_groups<-c()
diffs<-c()
for(i in 1:length(tmat))
{
 if(!(i %in% checked_groups))
 {
 mat1<-which(tmat[i] == tmat)
 py1<-which(tpy[i] == tpy)
 if(length(mat1) != length(py1) || sum(mat1-py1) != 0)
 {
     diffs<-append(diffs, i)
     
 }
  checked_groups<-append(checked_groups, mat1)
 }
}

diffs


i<-6

mat1<-which(tmat[i] == tmat)

py1<-which(tpy[i] == tpy)
 
nin<-!(py1 %in% mat1) 

pynums<-py1[nin]

#fpy[1,] - fpy[pynums,]
 
fpy[rep(i,length(pynums)),] - fpy[pynums,]

nin2<-(py1 %in% mat1)
pynums2<-py1[nin2]
 
fpy[rep(i,length(pynums2)),] - fpy[pynums2,]

fghfghgfh
fmat0[diffRows2,] - fpy0[diffRows2,]

fmat[diffRows2,] - fpy[diffRows2,]

#prob_row
p<-1502
#
max(fmat0[,14], na.rm=TRUE)

max(fpy0[,14], na.rm=TRUE)

min(fmat0[,14], na.rm=TRUE)

min(fpy0[,14], na.rm=TRUE)

lin_map<-function(val, min1, max1) {
 new_low = 1
 new_hi = 9
 
 
 new_low + ((val - min1) / (max1 - min1)) * (new_hi - new_low)
}

lin_map(5, 3, 36)

fmat0[p,]
fmat[p,]

fpy0[p,]
fpy[p,]

a<-c( 15,  20,  44,  39,   6,  28,  31,   3,  24,  18,  21,  65,  79,  53,
  19,  11,  19,   4,  22,  20,   3,  25,  38,  39,  38,  52,  79,  97,
  89,  67,  46,  37,  43,  65,  98, 135, 171, 196, 205, 205, 207, 216,
 226, 230, 226, 217, 212, 213, 215, 214, 208, 197, 185, 176, 172, 171,
 168, 167, 166, 167, 170, 171, 169, 162, 153, 148, 149, 159, 169, 171,
 157, 133, 110,  99, 103, 117, 130, 126, 102,  69.)
 
 b<-c(15,
    20,
    44 ,
    39  ,
     6   ,
    28    ,
    31     ,
     3      ,
    24       ,
    18        ,
    21         ,
    65          ,
    79           ,
    53            ,
    19             ,
    11              ,
    19               ,
     4                ,
    22                 ,
    20                  ,
     3                   ,
    25                    ,
    38                     ,
    39                      ,
    38                       ,
    52                        ,
    79                         ,
    97                          ,
    89                           ,
    67                            ,
    46                             ,
    37                              ,
    43                               ,
    65                                ,
    98                                 ,
   135                                  ,
   171                                   ,
   196                                    ,
   205                                     ,
   205                                      ,
   207                                       ,
   216                                        ,
   226                                         ,
   230                                          ,
   226                                           ,
   217                                            ,
   212                                             ,
   213                                              ,
   215                                               ,
   214                                                ,
   208                                                 ,
   197                                                  ,
   185                                                   ,
   176                                                    ,
   172                                                     ,
   171                                                      ,
   168                                                       ,
   167                                                        ,
   166                                                         ,
   167                                                          ,
   170                                                           ,
   171                                                            ,
   169                                                             ,
   162                                                              ,
   153                                                               ,
   148                                                                ,
   149                                                                 ,
   159                                                                  ,
   169                                                                   ,
   171                                                                    ,
   157                                                                     ,
   133                                                                      ,
   110                                                                       ,
    99                                                                        ,
   103                                                                         ,
   117                                                                          ,
   130                                                                           ,
   126                                                                            ,
   102                                                                             ,
    69)                                                                             
  
  pks<-c(3,
     7,
     9,
    13,
    17,
    19,
    24,
    28,
    44,
    49,
    62,
    70,
    77)
    
  plot(a, type="b")
  abline(v=39)                                                                                   
  points((1:length(a))[pks], a[pks], col="red", pch=2)
  
  dx = a[2:80] - a[1:79]

###merge clusters 
s2mat<-read.csv('C:\\Users\\richa\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\matlab_semi_final2.csv', header = FALSE)

s2py<-read.csv('C:\\Users\\richa\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\python_semi2.csv', header = FALSE)

s1mat<-read.csv('C:\\Users\\richa\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\matlab_semi_final1.csv', header = FALSE)

s1py<-read.csv('C:\\Users\\richa\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\python_semi1.csv', header = FALSE)


 