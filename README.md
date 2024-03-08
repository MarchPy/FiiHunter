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

O script gera uma lista filtrada de ativos financeiros, juntamente com recomendações e classificações com base nos critérios predefinidos. Os resultados são salvos em um arquivo Excel no diretório "resultados".

Lembre-se de modificar os caminhos e configurações específicas para atender às suas necessidades antes de executar o script.
