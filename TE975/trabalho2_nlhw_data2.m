Z= csvread('SNLS80mV.csv');
u= Z(:,1);
y=Z(:,1);
z= iddata(y, u, 1);
ze=z(500:2000); 
zv=z(2001:2100); 

figure(1)
plot (ze(101:200))

mhw1 = nlhw(ze,[15 10 1], pwlinear, unitgain, 'maxiter',2);
get(mhw1)
mhw2 = nlhw(ze,[2 3 1], pwlinear, unitgain, 'maxiter',2);
get(mhw2)
mhw3 = nlhw(ze,[3 15 1], pwlinear, unitgain, 'maxiter',2);
get(mhw3)

obtained_model1 = pem(ze, mhw1);
obtained_model2 = pem(ze, mhw2);
obtained_model3 = pem(ze, mhw3);

figure(2)
compare(zv, mhw1, mhw2, mhw3)
grid on

%InputNonlinearity

mhw_non1 = idnlhw([15 10 1], 'wavenet', 'pwlinear');
ME1 = nlhw(ze, mhw_non1);
get(ME1)

mhw_non2 = idnlhw([3 15 1], 'wavenet', 'pwlinear');
ME2 = nlhw(ze, mhw_non2);
get(ME2)

obtained_model_non1 = pem(ze, ME1);
obtained_model_non2 = pem(ze, ME2);

figure(3)
compare(zv, ME1, ME2)
grid on
