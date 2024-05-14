
clear
clc

% test spike separtor
%S_block = sig %[1.2 2.3 0.5; 0.4 1.3 -1.2; 0.1 -2.3 1.2; -0.4 0.3 -1.0; -0.2 0.3 0.2];
%template = tmp %[4.2 -1.3 0.1; 0.3 -1.2 -0.2];
S_neighbor = 4;
window = 2;
TH = 1;
S_block = [ 1 2 1 3 1 1 1 1 2 1 7 3 1 7 1 3 1  5 7 1 2 1 1 1 1 1 1 ];
template = [1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1];

S_block 
template

[S_block, template] = spike_seperator(S_block, template, S_neighbor, window, TH);

S_block 
template

%stopdsfsdf

% test MatLab functions, to be compared to results given from "test_python_functions.py"
clear
clc

format long

% length of vector to test
l = 70;
% test vector
vec = 1:l;

% convert to column vector
vec= vec(:);

sig_one_loc = [2.05380473 2.00346509 2.16420290 1.93650801 1.73023771 1.62974612 1.83129045 1.73825459 1.50134206 1.37226018 1.21029930 0.99399786 0.56131853...
    0.62502478  0.40421832  0.15179104 -0.19984990  0.13538237 -0.36996807 -0.57770386 -0.80223724 -0.95300019 -1.02083985 -1.04877257...
 -1.29854160 -1.30681311 -1.80474173 -1.24239579 -1.67209278 -1.74635780 -1.65893378 -1.54706756 -1.63684419 -1.55158290 -1.40013536 -1.57844632...
 -1.91095723 -1.30543562 -1.35765670 -1.61231483 -0.86602634 -1.49685347 -0.60214273 -0.66969391 -0.35225514 -0.32151752 -0.32857566 -0.12354467...
 -0.10404514  0.26808610  0.29360745  0.25647750  0.81849265 0.73729079 0.80275118 0.95879203  0.90606765  1.10996522  1.34009400  1.58806069...
  1.35338891  1.76951629  1.03496085  1.14905657  1.45796965 1.31203815 1.32102916 1.31759934  1.55042257  1.32887788  0.96204821  0.82551381...
  0.73226371  0.72042820  0.64252875  0.66966656  0.39154753 0.17119368 0.49057574 0.01689638 -0.30318896 -0.04490348 -0.20367729 -0.12539701...
 -0.31721096 -0.86676738 -0.58863505 -0.60351439 -0.72255613 -0.94367153 -0.87755994];

sig1 = [1.33292319  1.29521846  1.28794477  0.78584047  1.18755056  0.63093354...
   1.31784033  0.38696084  0.41366058  0.37575635  0.19579819  0.29269415...
 -0.12657596 -0.08116249  0.01096527 -0.57750902 -0.34837561 -0.36660056...
 -1.13232701 -0.69985967 -0.82749987 -0.83259747 -0.58853683 -1.32413818...
 -0.75576848 -1.17868596 -1.29289256 -1.14169417 -0.90720613 -1.17503335...
 -0.84553414 -0.93687339 -0.92283593 -0.79054949 -0.67869351 -0.84664096...
 -0.41994362 -0.52751801 -0.03800074 -0.38347728 -0.41129663  0.31871805...
  0.15888794  0.21100095  0.17614914  0.29002043  0.48280234  0.62847307...
  0.41588578  0.75480570  0.96893000  0.64067695  0.67276726  0.45364116...
  0.71881804  0.65838892  0.59324065  0.66629152  0.92457958  0.62278248...
  0.98379437  0.52619467  0.50052299  0.51043046  0.30718994  0.21387227...
  0.23516907  0.15372401  0.49406358  0.17275069 -0.14364538 -0.01912809...
 -0.14907070 -0.18038856  0.03396831 -0.14229613 -0.06158262 -0.20695152...
 -0.74196550 -0.16887568 -0.10751462 -0.45156213 -0.68774019 -0.30076820...
 -0.62219248 -0.55542883 -0.19676822 -0.64345331 -0.14097269 -0.40662118...
 -0.02454941];

sig2 = [0.762990366  0.998337101  0.462281847  0.970245178  1.107454926...
  1.105069425  0.912473516  1.226742729  1.108549966  1.445098205...
  1.412796701  1.437034976  1.927739210  1.832516875  1.788885559...
  2.067804215  1.960773832  1.610234557  2.121970337  1.673729160...
  1.488772013  1.048554888  0.367886909 -0.300466785 -0.398848565...
 -0.484877690 -0.897332099 -1.558575902 -1.996260523 -2.231224942...
 -2.232420277 -2.548305533 -2.838792308 -2.811515744 -2.822574003...
 -2.862471394 -2.746537175 -2.645199874 -2.405337979 -1.706049778...
 -1.805307189 -1.321446754 -1.140220950 -0.809728479 -0.445898560...
 -0.692801416 -0.175286423 -0.454761076 -0.204285399 -0.217942804...
  0.129663709  0.416722310  0.355718583  0.006421362  0.006711822...
  0.078906904 -0.343636196 -0.143728131  0.309366200 -0.103006849...
  0.269020296  0.517454453  0.640257643  0.842740791  1.422651154...
  1.332407176  1.712744117  2.125166923  2.268467447  2.413350183...
  2.569196680  2.981288874  2.815292502  2.662880512  2.528700135...
  2.600876315  2.292643104  2.265962360  1.590090350  1.570278436...
  1.476823510  0.823215366 -0.171170882  0.158993561 -0.438714517...
 -0.935473024 -1.193041454 -1.746833490 -1.494147814 -1.825406248...
 -2.117284088];
 
 sig3 = [1.84900416  1.77607846  1.95684115  2.59663693  3.03510151  3.33337422...
  3.42429924  3.67813964  3.90475410  3.57971889  3.40873382  3.24305099...
  2.99658766  2.01400397  1.82544707  1.00536668  0.66669704  0.65309323...
  0.25378941 -0.26211103 -0.31709457 -0.68696508 -0.02210882 -0.75562610...
 -0.29175660 -0.37596255 -0.14162170 -0.28013046 -1.04351926 -1.41874639...
 -1.40617060 -1.97581332 -2.57938847 -3.27438408 -3.62030123 -3.56272999...
 -4.19431154 -3.82358060 -4.13089117 -3.47478599 -3.08707372 -2.88877000...
 -2.33504115 -2.21462070 -1.82549980 -0.99664612 -0.82406208 -0.60777273...
 -0.37831295 -0.79275903 -0.63829040 -0.57657753 -0.72270126 -0.61944558...
 -0.50483993  0.03958881 -0.04708685  0.61486900  1.13211466  1.50886761...
 2.09279430  2.72433003  3.02713890  3.41143538  3.60868676  3.48224930...
 3.93848123  3.25651508  3.19259800  3.08493124  2.72376362  2.55704557...
 2.04803537  1.57628719  1.74559570  1.36661292  1.46439030  1.30363796...
 1.67806165  1.84346906  1.31598357  1.09448499  1.59906450  1.46218289...
 1.17711161  0.23899846  0.35462642 -0.59044077 -1.31069161 -1.77566813...
 -2.40377939];
 
 sig4 = [3.122963323  4.186998898  4.593987478  4.672681764  4.898433319...
 4.769318013  4.395092417  3.884970926  3.621901806  3.156807028...
 2.586292722  2.387324238  2.292241157  2.377648950  2.354041667...
 2.582301197  2.572035018  2.340921727  2.572134693  1.715842072...
 1.119500472  0.095417334 -0.528201197 -1.424309660 -2.413684797...
-2.413774681 -2.696542388 -2.788513794 -2.829921035 -2.604472534...
-2.217983264 -2.692848977 -2.747405595 -2.608809126 -3.095487688...
-3.515195244 -4.244378764 -4.543045779 -5.142687120 -5.055129906...
-4.690220796 -4.275341284 -3.717861189 -2.928282286 -2.274474849...
-1.863971122 -1.483759134 -1.190040472 -1.339129606 -1.424807439...
-0.960655690 -1.284027505 -1.445227358 -1.315565162 -0.303599099...
 0.547888141  0.776223170  1.843292436  2.340200752  2.937794608...
 3.592547460  3.766108019  3.349174607  3.548187724  3.029598781...
 3.461248950  2.979256534  2.596484451  2.904687516  3.251225484...
 3.779167244  3.777327674  4.166664338  4.455862952  4.377831630...
 4.128366203  3.588615242  2.967434930  1.889366689  1.314685411...
 0.751781717  0.176047085 -0.032452214 -0.104039204  0.007670046...
-0.004506773 -0.202303097  0.154745789 -0.602640125 -0.646093759...
-1.474984970];

sig = vertcat(sig1, sig2, sig3, sig4);

%%%%%%%%%%%%%%%%%%%%%%

% offset
k = 1;

disp("out1:");
out1 = runningTEO(vec, k);
disp(out1)

%%%%%%%%%%%%%%%%%%%%%%
ks = [2 3 5];


[runTEO, tmp] = MTEO(vec, ks);

disp("MTEO(vec, ks) =");
disp(runTEO);
disp("tmp = ")
disp(tmp);
disp(size(tmp));

%%%%%%%%%%%%%%%%%%%%%%%
template = tmp(1, :);

lag = 10;

sig5 = [sig1 0]
sig6 = [0 sig1]
sig5(10) = 1

[PsC_s,best_lag] = PsC(sig5,sig6,lag);
disp("PsC(template,sig,lag) = ")
disp("PsC_s = ")
disp(PsC_s)
disp("best_lag = ")
disp(best_lag)

[PsC_s2,best_lag2] = PsC(sig6,sig5,lag);
disp("PsC_s2 = ")
disp(PsC_s2)
disp("best_lag2 = ")
disp(best_lag2)


%%%%%%%%%%%%%%%%%%%%%%%

locs = [2, 4];
TH = 0.2;
Fs = 3000;

[loc,new_sig] = findspikes(template,sig,locs,Fs,TH);

disp("findspikes(template,sig,locs,Fs,TH) = ")
disp("loc = ")
disp(loc)
disp("new_sig = ")
disp(new_sig)

%%%%%%%%%%%%%%%%%%%%%%%

DTh = 0.1;
Fs = 3000;

TE = resolve_peaks(sig_one_loc, DTh, Fs);

disp("resolve_peaks(sig, DTh, Fs) = ");
disp(TE);

[ans, locs] = findpeaks(sig_one_loc);
disp("findpeaks(sig_one_loc)");
disp(locs);
disp(ans);


%%%%%%%%%%%%%%%%%%%%%%%%%
ks = [2 3 5];
L = 0.01;
Fs = 3000;
disp(size(runTEO))

[TE,DTh] = MTH(runTEO,ks,L,Fs);

disp("MTH(MTEO,ks,L,Fs) = ");
disp(TE);
disp(DTh);

%%%%%%%%%%%%%%%%%%%%%%%%%
S_block = sig %[1.2 2.3 0.5; 0.4 1.3 -1.2; 0.1 -2.3 1.2; -0.4 0.3 -1.0; -0.2 0.3 0.2];
template = tmp %[4.2 -1.3 0.1; 0.3 -1.2 -0.2];
S_neighbor = 3;
window = 2;
TH = 0.2;

[S_block, template] = spike_seperator(S_block,template,S_neighbor,window,TH);
disp("spike_seperator(S_block,template,S_neighbor,window,TH) = ");
disp(S_block);
disp("template =");
disp(template);

%%%%%%%%%%%%%%%%%%%%%%%%%
S_block = sig(1, :)
template = tmp(1, :)
TH = 0.2
TH1 = 0.4

features = border_detector(S_block,template,TH,TH1)
disp("border_detector(S_block,template,TH,TH1) = ");
disp(features);

%%%%%%%%%%%%%%%%%%%%%%%%%%%
Fs = 3000;
Notch = 0;

[sig,Fs] = initialize(sig_one_loc,Fs,Notch);

disp("initialize(sig_one_loc,Fs,Notch) = ");
disp(sig);
disp("Fs =");
disp(Fs);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
original_range = [-2.5, 2.5];
map_range = [-100.5, 100.5];

Y = linear_map(sig_one_loc, original_range, map_range);
 
disp("linear_map(sig_one_loc, original_range, map_range) = ");
disp(Y);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

features = round(features)
features2 = vertcat(features, features, features)%, features, features); %, features)

fea1 = [2     2     2     2   NaN     2     2     2     2   NaN     4     3     3   NaN     1     1     1     1   NaN     2     5     6     9   NaN]
fea2 = [2     2     2     2     2     2     2     2     2     2     3     3     3     1     1     1     1     1     1     1     3     4     6     6]
fea3 = [2     2     2     2     2     2     2     2     2     1     2     1     3     3     1     1     1     1     1     2     3     3     4     6]
fea4 = [2     2     2     2     1     2     2     2     2   NaN     4     3     3   NaN     1     1     1     1   NaN     2     5     6     9   NaN]
fea5 = [2     2     2     2     2     2     2     2     2     2     3     3     3     1     1     1     1     1     1     1     3     4     6     6]
fea6 = [2     2     2     2     2     2     2     2     2     1     2     1     3     3     1     1     1     1     1     2     3     3     4     6]

features3 = vertcat(fea1, fea2, fea3, fea4, fea5, fea6)
     
%features2(2, 2) = 1 % 2 to be the same
%features2(2, 7) = 2 # 2, 3, 4 to be the same
%features2(2, 21) = np.NaN # 2 to be the same
%features2(1, 7) = 2;
%features2(2, 7) = 3;
%features2(3, 7) = 4;

%features2(4, 21) = 1;
%features2(5, 21) = 2;

%features2(4, 5) = 14
%features2(5, 5) = 13 %0.318718050000000
%features2(4, 7) = 5

title = generate_title(features2);

disp("generate_title(features3) = ");
disp(title);

%gyugyug
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

template = tmp; 
%title = 1:3;
TH = 0.2;
Fs = 3000;
sig_l = 500;

uniq_c = merge_clusters(template,title,TH,Fs,sig_l);

disp("merge_clusters(template,title,TH,Fs,sig_l) = ");
disp(uniq_c);
size(uniq_c)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%, C = 0.1, threshold_PsC = 0.1, init = True, wind = 0.020
sampling_freq = 3000;

[Index, loc] = TK_filter(sig, sampling_freq);

disp("TK_filter(sig, sampling_freq) = ");
disp(Index)
disp("loc =")
disp(loc)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
peaks = findpeaks(abs(sig_one_loc))

disp("Find peaks = ")
disp(peaks)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
a = [1 2 1 0 15  20  44  39   6  28  31   3  24  18  21  65  79  53 19  11  19   4  22  20   3  25  38  39  38  52  79  97 89  67  46  37  43  65  98 135 171 196 205 205 207 216 226 230 226 217 212 213 215 214 208 197 185 176 172 171 168 167 166 167 170 171 169 162 153 148 149 159 169 171 157 133 110  99 103 117 130 126 102  69];

peaks = findpeaks(a)%, edge='falling')

disp("detect_peaks(a) = ")
disp(peaks)



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Channel 59 data
%MUs found: 27 via channel: 59
clear
clc

%test_data = readmatrix('C:\Users\richa\OneDrive - Newcastle University\RSE\Micro-EMG\Micro-EMG-analysis\microEMG-software\analysis_software\analysis\tests\test_data.csv'); 
%test_data = readmatrix('C:\Users\nrajh\OneDrive - Newcastle University\RSE\Micro-EMG\Micro-EMG-analysis\microEMG-software\analysis_software\analysis\tests\test_data.csv'); 

% try data that returns 1 MU in python, data processed by GS and then
% channel 22 selected for highest SNR
test_data = readmatrix('C:\Users\nrajh\OneDrive - Newcastle University\RSE\Micro-EMG\Micro-EMG-analysis\microEMG-software\analysis_software\analysis\tests\py_used_data_chn_22.csv'); 

tic
[index,loc,temps] = TK_filter(test_data,20000,0.1,0.1,1,0.004,0);
toc

%writematrix(index,"C:\Users\richa\OneDrive - Newcastle University\RSE\Micro-EMG\Micro-EMG-analysis\microEMG-software\analysis_software\analysis\tests\results_matlab_index_chn22.csv"); 
%writematrix(loc,"C:\Users\richa\OneDrive - Newcastle University\RSE\Micro-EMG\Micro-EMG-analysis\microEMG-software\analysis_software\analysis\tests\results_matlab_locs_chn22.csv"); 
writematrix(index,"C:\Users\nrajh\OneDrive - Newcastle University\RSE\Micro-EMG\Micro-EMG-analysis\microEMG-software\analysis_software\analysis\tests\results_matlab_index_chn22.csv"); 
writematrix(loc,"C:\Users\nrajh\OneDrive - Newcastle University\RSE\Micro-EMG\Micro-EMG-analysis\microEMG-software\analysis_software\analysis\tests\results_matlab_locs_chn22.csv"); 

%disp('index =')
%disp(index)
%disp('loc =')
%disp(loc)
%disp('temps =')
%disp(temps)

disp(['MUs found: ' num2str(max(loc)) ' via channel: 22']);

%disp(['MUs found: ' num2str(max(loc)) ' via channel: 59']);



