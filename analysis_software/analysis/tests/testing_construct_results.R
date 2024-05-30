name<-"nrajh"

motor_unit_number<-0
extra_label = "_highest3_" #"_filters2_" #"_highest2_" #"_filters_" #"""_v1_"

extra_label2<-"(max filters)" #"(highest peak)"

py_fibre_locs<-read.csv(paste0('C:\\Users\\',name,'\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\py_fibre_centres',extra_label,motor_unit_number ,'.csv'), header = FALSE)#, nrows=80000)

mat_fibre_locs<-read.csv(paste0('C:\\Users\\',name,'\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\fibre_centres',(motor_unit_number + 1) ,'.csv'), header = FALSE)#, nrows=80000)

#ymax<-max(c(py_fibre_locs[,2], mat_fibre_locs[,2]))
#ymin<-min(c(py_fibre_locs[,2], mat_fibre_locs[,2]))
#xmax<-max(c(py_fibre_locs[,1], mat_fibre_locs[,1]))
#xmin<-min(c(py_fibre_locs[,1], mat_fibre_locs[,1]))

xmin<-(-1)
xmax<-21.5
ymin<--5.4
ymax<--ymin

cext<-2

dev.new()
par(mar=c(5,5,4,2) + 0.1)  #bltr
plot(py_fibre_locs, main=paste0("Python ",extra_label2,", motor unit ", (motor_unit_number+1)), cex=0.5, xlab="Position (mm)", ylab="Position (mm)", xlim=c(xmin, xmax), ylim=c(ymin,ymax), cex.axis=cext, cex.main=cext, cex.lab=cext)

dev.new()
par(mar=c(5,5,4,2) + 0.1)
plot(mat_fibre_locs, main=paste0("MATLAB, motor unit ", (motor_unit_number+1)), cex=0.5, xlab="Position (mm)", ylab="Position (mm)", xlim=c(xmin,xmax), ylim=c(ymin,ymax), cex.axis=cext, cex.main=cext, cex.lab=cext)

