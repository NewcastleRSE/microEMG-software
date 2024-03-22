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

fpy0<-read.csv('C:\\Users\\richa\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\features0_python_pre_gen_titles.csv', header = FALSE, nrows=2000)

fmat0<-read.csv('C:\\Users\\richa\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\features0_matlab_pre_gen_titles.csv', header = FALSE, nrows=2000)

fpy<-read.csv('C:\\Users\\richa\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\features_python_pre_gen_titles.csv', header = FALSE, nrows=2000)

fmat<-read.csv('C:\\Users\\richa\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\features_matlab_pre_gen_titles.csv', header = FALSE, nrows=2000)

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
