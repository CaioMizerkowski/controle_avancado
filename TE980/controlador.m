% Programa original em Matlab disponibilizado pelo professor
% Controlador PI adaptativo indireto de Camacho et al. (1992)
clear all
close all
clc
 
A = 0.15;   % parâmetro de projeto do controlador (a ser otimizado)
 
% iniciação dos parâmetros dos mínimos quadrados recursivo
tetac   = [0.1  0.1  0.1];                     % estimativa inicial para os valores de a's e b's
niter   = 600;                                     % número de iterações
Minic   = 100;                                    % matriz de covariância inicial
M       = Minic * eye(size(tetac,2));    % iniciação da matriz de covariância

% foram estipuladas 3 referências diferentes (análise de comportamento servo)
yr(1,001:200)   = 4;    % referência (valor desejado para a saída do processo)
yr(1,201:400)   = 3;    % referência (valor desejado para a saída do processo)
yr(1,401:niter) = 5;    % referência (valor desejado para a saída do processo)
 
% escalonamento de acordo com a mudança de referência (usa no ITAE)
r( 001: 200)   = 1; 
r( 201: 400)   = 2; 
r( 401: niter) = 3; 
 
y(1,1:3)    = 0;      % inicia a saída do processo
dy(1,1:3)   = 0;      % inicia a variação da saída do processo
u(1,1:3)    = 0;      % inicia a ação de controle
du(1,1:3)   = 0;      % inicia a variação da ação de controle

e(1,1:3)      = 0;      % inicia o erro do modelo incremental Deltay
erro(1,1:3)  = 0;      % inicia o erro do modelo posicional y
d                = 4;      % inicia o laço principal
ts               = 0.1;    % período de amostragem
u_max       = 20;     % limite máximo para a ação de controle
u_min        = 0;      % limite mínimo para a ação de controle
 
ITAE            = zeros(size(unique(r),2),1);   % no. de refs diferentes x niter

% laço principal
for k = d:niter       % controlar para niter iterações (amostras)
   
   % saída do processo, y
   y(k) = 0.0025*u(k-1) + 0.9936*y(k-1);     % processo bola e tubo
   % variação da saída  (modelo incremental em vez de posicional)
   dy(k) = y(k) - y(k-1);
 
   %- início ------------------------------- MQR
   % vetor de regressores para o mínimos quadrados recursivo
   psi = [dy(k-1) du(k-2) du(k-3)];
   % erro do modelo matemático estimado para o real (modelo incremental)
   erro(k) = dy(k) -  psi*tetac';  
   % atualização das equações dos mínimos quadrados recursivo
   ganho = M*psi'/(1 + psi*M*psi');
   tetac = tetac + ganho'*erro(k);
   M     = (M - M*psi'*psi*M / (1 +psi*M*psi'));
   TM(k) = trace(M);       % soma elementos da diagonal principal

   % atualiza vetor de estimativas 
   a1(k) = tetac(1);   
   b0(k) = tetac(2);    
   b1(k) = tetac(3);
   guarda_tetac(k,:) = tetac;
   %- final ------------------------------- MQR
 
   e(k)  = yr(k) - y(k);     % erro da saída do processo 
  
   % cálculo da lei de controle (ver artigo do Camacho)
   g0(k) = A*A*(1-A) / [A*b0(k)+b1(k)];
   du(k) = g0(k) * [e(k) - a1(k)*e(k-1)];
   % ação de controle INCREMENTAL a ser aplicada ao processo
   u(k)  = u(k-1) + du(k);
   % saturador (limita os valores de ação de controle)
   if u(k) > u_max,          u(k) = u_max;       end   
   if u(k) < u_min,          u(k) = u_min;       end   
   
   if r(k) ~= r(k-1)
     ITAE(r(k)) = 0;    
   end

   ITAE(r(k)) = ITAE(r(k)) + (k-d+1)*abs(erro(k));

end
%--------------------- resultados
mostra_resultados = 1;
if mostra_resultados
    fprintf('Controlador PI adaptativo indireto de Camacho et al. (1992):\n');
     fprintf('\nA: %f\n',A);
    % critérios de desempenho
    % IAE: Integral of Absolute Error
    fprintf('\nIAE  = %f\n', sum( abs (erro(d:niter)) ));
    %  ITAE: Integral of Time multiply by Absolute Error
    fprintf('\nITAE = %f\n', sum(ITAE));
    % Variância do sinal de controle
    fprintf('\nVariância do sinal de controle = %f\n\n\n', var(u(d:niter)));
   
    % gráficos 
    figure(1);     t = (0:ts:niter*ts-ts)';
    subplot(2,2,1), plot(t,y,t,yr),title('saída do processo'); ylabel('saída'),xlabel('tempo (s)');
    subplot(2,2,2), plot(t,u), title ('ação de controle'); ylabel('controle'),xlabel('tempo (s)');
    
    subplot(2,2,3), plot(1:length(TM(d:niter)),TM(d:niter)), 
                    title ('traço da matriz de covariância'); ylabel('traço'),xlabel('tempo (s)');
    subplot(2,2,4), plot(1:length(guarda_tetac(d:niter)),guarda_tetac(d:niter,:)), 
                    title ('parâmetros estimados pelo mínimos quadrados recursivo'); ylabel('\theta'),xlabel('tempo (s)');
                    legend('a_1_e','b_0_e','b_1_e');
end
 


   
   