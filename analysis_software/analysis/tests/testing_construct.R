name<-"richa" #"nrajh"

spikes_mat<-read.csv(paste0('C:\\Users\\',name,'\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\spikes_matlab.csv'), header = FALSE)#, nrows=80000)

spikes_py<-read.csv(paste0('C:\\Users\\',name,'\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\spikes_python.csv'), header = FALSE)#, nrows=80000)

head(spikes_mat)

head(spikes_py)

sum(spikes_mat - spikes_py)




sig_mat<-read.csv(paste0('C:\\Users\\',name,'\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\sig_matlab.csv'), header = FALSE)#, nrows=80000)

sig_py<-read.csv(paste0('C:\\Users\\',name,'\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\sig_python.csv'), header = FALSE)#, nrows=80000)

head(sig_mat)

head(sig_py)

sum(sig_mat - sig_py)



b_mat<-read.csv(paste0('C:\\Users\\',name,'\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\b_findpeaks_2d_matlab.csv'), header = FALSE)#, nrows=80000)

b_py<-read.csv(paste0('C:\\Users\\',name,'\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\b_findpeaks_2d_python.csv'), header = FALSE)#, nrows=80000)

head(b_mat)

head(b_py)

sum(b_mat - b_py)

##


im_mat<-read.csv(paste0('C:\\Users\\',name,'\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\im_findpeaks_2d_matlab.csv'), header = FALSE)#, nrows=80000)

im_py<-read.csv(paste0('C:\\Users\\',name,'\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\im_findpeaks_2d_python.csv'), header = FALSE)#, nrows=80000)

head(im_mat)

head(im_py)

image(as.matrix(im_mat), useRaster=TRUE, axes=FALSE, main="MATLAB")

dev.new()
image(as.matrix(im_py), useRaster=TRUE, axes=FALSE, main="Python")

sum(im_mat - im_py)

###


im2_mat<-read.csv(paste0('C:\\Users\\',name,'\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\im2_findpeaks_2d_matlab.csv'), header = FALSE)#, nrows=80000)

im2_py<-read.csv(paste0('C:\\Users\\',name,'\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\im2_findpeaks_2d_python.csv'), header = FALSE)#, nrows=80000)

head(im2_mat)

head(im2_py)

sum(im2_mat - im2_py)


image(as.matrix(im2_mat), useRaster=TRUE, axes=FALSE, main="MATLAB 2")

dev.new()
image(as.matrix(im2_py), useRaster=TRUE, axes=FALSE, main="Python 2")


peaks_mat<-read.csv(paste0('C:\\Users\\',name,'\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\locs_findpeaks_2d_matlab.csv'), header = FALSE)#, nrows=80000)

peaks_py<-read.csv(paste0('C:\\Users\\',name,'\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\locs_findpeaks_2d_python.csv'), header = FALSE)#, nrows=80000)


peaks2_mat<-read.csv(paste0('C:\\Users\\',name,'\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\locs2_findpeaks_2d_matlab.csv'), header = FALSE)#, nrows=80000)

peaks2_py<-read.csv(paste0('C:\\Users\\',name,'\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\locs2_findpeaks_2d_python.csv'), header = FALSE)#, nrows=80000)
           
ymax=dim(im2_mat)[1]
xmax=dim(im2_mat)[2]

dev.new()
image(t(as.matrix(im2_mat)), useRaster=TRUE, axes=TRUE, main="MATLAB")
points(peaks_mat[,1]/xmax, peaks_mat[,2]/ymax, col="black", pch=4, cex=5, lwd=2)

#dev.new()
#image(t(as.matrix(im2_mat)), useRaster=TRUE, axes=TRUE, main="MATLAB 2")
#points(peaks2_mat[,1]/xmax, peaks2_mat[,2]/ymax, col="black", pch=4, cex=5, lwd=2)

ymaxp=dim(im2_py)[1]
xmaxp=dim(im2_py)[2]

dev.new()
image(t(as.matrix(im2_py)), useRaster=TRUE, axes=TRUE, main="Python 1")
points(peaks_py[,1]/xmaxp, peaks_py[,2]/ymaxp, col="black", pch=4, cex=5, lwd=2)


#dev.new()
#image(t(as.matrix(im2_py)), useRaster=TRUE, axes=TRUE, main="Python 2")
#points(peaks2_py[,1]/xmax, peaks_py[,2]/ymax, col="black", pch=4, cex=5, lwd=2)


name<-"nrajh"

im2_py<-read.csv(paste0('C:\\Users\\',name,'\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\im2_findpeaks_2d_python.csv'), header = FALSE)#, nrows=80000)

peaks_py<-read.csv(paste0('C:\\Users\\',name,'\\OneDrive - Newcastle University\\RSE\\Micro-EMG\\Micro-EMG-analysis\\microEMG-software\\analysis_software\\analysis\\tests\\locs_findpeaks_2d_python.csv'), header = FALSE)#, nrows=80000)

#peaks_py<-t(peaks_py)

ymaxp=dim(im2_py)[1]
xmaxp=dim(im2_py)[2]

dev.new()
image(t(as.matrix(im2_py)), useRaster=TRUE, axes=TRUE, main="Python 1")
points((peaks_py[,1]+1)/xmaxp, (peaks_py[,2]+1)/ymaxp, col="black", pch=4, cex=5, lwd=2)


a<-max(im2_py)

rowMaxs(im2_py)

(im2_py)





