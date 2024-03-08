## _FundsExplporer_ - Introdução ao programa

Este script coleta e analisa dados de ativos financeiros, mais especificamente fundos de investimento imobiliário (FIIs) no Brasil. Ele extrai informações do site 'fundamentus.com.br' e, em seguida, processa e filtra os dados para análises posteriores. Aqui está uma visão geral do código e de suas funcionalidades:

## Uso:

Para usar este script, siga estas etapas:

1. Certifique-se de ter as bibliotecas Python necessárias instaladas. Você pode usar o arquivo `requirements.txt` para instalá-las.
2. Defina seus critérios de investimento no arquivo `config/settings.json`.
3. Execute o script executando-o em seu ambiente Python

   ```bash
   python3 main.py -s 
   ```

   .

## Saída:

O script gera uma lista filtrada de ativos financeiros com base nos critérios predefinidos. Os resultados são salvos em um arquivo Excel no diretório "resultados".


**FII:** Sigla para Fundo de Investimento Imobiliário. São investimentos que aplicam em renda fixa e variável, através de um portfólio de imóveis, como lajes corporativas, shopping centers, galpões logísticos, etc.

**Nome:** Nome oficial do Fundo de Investimento Imobiliário.

**Segmento:** Área de atuação do FII, como:

* **Renda:** Aluguel de imóveis (escritórios, shopping centers, etc.).
* **Híbrido:** Aluguel e desenvolvimento de imóveis.
* **Tijolo:** Desenvolvimento de imóveis para venda.
* **Papéis:** Investimento em títulos do mercado imobiliário.

**Cotação:** Preço atual de cada cota do FII na bolsa de valores.

**Min 52 sem:** Menor preço da cota nos últimos 52 semanas.

**Max 52 sem:** Maior preço da cota nos últimos 52 semanas.

**Vol $ méd (2m):** Volume médio de negociação em dólares nos últimos 2 meses.

**Valor de mercado:** Valor total do FII, calculado pela cotação multiplicada pelo número de cotas.

**Nro. Cotas:** Número total de cotas do FII em circulação.

**FFO Yield:** Retorno do FII em relação ao seu valor patrimonial, considerando o FFO (Funds From Operations).

**Div. Yield:** Retorno do FII em dividendos, considerando a cotação e os dividendos distribuídos nos últimos 12 meses.

**P/VP:** Relação entre o preço da cota e o valor patrimonial do FII.

**Ativos:** Valor total dos investimentos do FII em imóveis e outros ativos.

**FFO/Cota:** Retorno do FII por cota, considerando o FFO.

**Dividendo/cota:** Valor dos dividendos distribuídos por cota nos últimos 12 meses.

**VP/Cota:** Valor patrimonial do FII por cota.

**Patrim Líquido:** Valor total dos bens do FII menos seus passivos.

**Qtd imóveis:** Número de imóveis no portfólio do FII.

**Qtd Unidades:** Número de unidades locatícias nos imóveis do FII.

**Imóveis/PL do FII:** Relação entre o número de imóveis e o valor patrimonial do FII.

**Área (m2):** Área total dos imóveis do FII em metros quadrados.

**Aluguel/m2:** Valor médio do aluguel por metro quadrado nos imóveis do FII.

**Preço do m2:** Valor médio do metro quadrado dos imóveis do FII.

**Cap Rate:** Taxa de retorno do investimento em um imóvel, considerando o aluguel e o valor do imóvel.

**Vacância Média:** Percentual de área locável desocupada nos imóveis do FII.


Lembre-se de modificar os caminhos e configurações específicas para atender às suas necessidades antes de executar o script.
