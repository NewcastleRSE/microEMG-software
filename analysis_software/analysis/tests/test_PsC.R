pc<-function(template, sig, lag0) { 

 m = length(template)
 n = length(sig)
 
  sig = c(rep(0, lag0), sig, rep(0, 2 * lag0))
    
 PsC_sc_max = 0
 min_lag = 0 + 1
 if(m <= lag0)
 {
     min_lag = lag0 - m
 }
     
 max_lag = 2 * lag0
 if(max_lag > n + lag0)
 {
     max_lag = n + lag0
  }
 
 for(k in 1:(2*lag0)) #min_lag:max_lag)
 {
     shifted_sig = sig[k:(k + m - 1)]
     #print(length(shifted_sig))
     p1 = template * shifted_sig
     p2 = abs(template - shifted_sig)
     p3 = pmax(abs(template), abs(shifted_sig))
     p4 = p1 - p2 * p3
     #normaliz = p3 * p3
    
     sum_p4 = sum(p4)
     print(" ")
     print(k)
      #print(sum_p4)
     print("vecs...")
     print(template)
     print(shifted_sig)
     if(sum_p4 > 0)
     {
         PsC_score = sum_p4/sum(p3 * p3)
         if(PsC_score > PsC_sc_max)
         {
             PsC_sc_max = PsC_score
         }
     }
  }       
     #    PsC_score[k] = 0
     #else:
     #    PsC_score[k] = sum_p4/np.sum(p3 * p3)
               
 #best_lag = np.nanargmax(PsC_score)
 #PsC_s = PsC_score[best_lag]
 #best_lag = best_lag - lag
 PsC_sc_max
}
 
 
temp<-c(0, 1, 2, 2, 3, 3, 1, 1, 2, 2, 3, -3)

sig<-c(1, -1.1, 2.2, 2, 3, 3.2, 0, -1, 2, -2, 3, 3)

lag0<-6

a<-pc(temp, sig, lag0) 

b<-pc(sig, temp, lag0) 

a
b

temp<-1:10
sig<-11:20

lag0<-2

a<-pc(temp, sig, lag0) 

b<-pc(sig, temp, lag0) 

a
b


