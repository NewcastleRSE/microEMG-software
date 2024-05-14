name<-"nrajh"

motor_unit_number<-0
extra_label = "_filters_" #"""_v1_"

py_fibre_locs<-read.csv(paste0('C:\\Users\\',name,'\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\py_fibre_centres',extra_label,motor_unit_number ,'.csv'), header = FALSE)#, nrows=80000)

mat_fibre_locs<-read.csv(paste0('C:\\Users\\',name,'\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\fibre_centres',(motor_unit_number + 1) ,'.csv'), header = FALSE)#, nrows=80000)

ymax<-max(c(py_fibre_locs[,2], mat_fibre_locs[,2]))
ymin<-min(c(py_fibre_locs[,2], mat_fibre_locs[,2]))

dev.new()
plot(py_fibre_locs, main=paste0("Python, motor unit ",extra_label, (motor_unit_number+1)), cex=0.5, xlab="Position (mm)", ylab="Position (mm)", ylim=c(ymin,ymax))

dev.new()
plot(mat_fibre_locs, main=paste0("MATLAB, motor unit ", (motor_unit_number+1)), cex=0.5, xlab="Position (mm)", ylab="Position (mm)", ylim=c(ymin,ymax))

