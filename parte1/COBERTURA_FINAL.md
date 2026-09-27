# Parte 1, Tarefa 1.6, Relatório de Cobertura Final

Autor, João Ricardo Magalhães Oliveira
Disciplina, Engenharia de Software II
Data, 26/09/2026

## 1. Comando executado

uv run pytest --cov=flaskbb.user --cov-report=term-missing


## 2. Resultado da suíte completa

246 testes coletados, 245 aprovados, 1 reprovado, a mesma falha pré-existente de tradução já registrada em `parte1/BASELINE.md` (`test_flaskbbdomain_translations`), sem nenhuma relação com o trabalho desta Parte 1.

## 3. Comparação com a baseline e a meta

| Arquivo | Baseline (Tarefa 1.1) | Final (Tarefa 1.6) | Variação |
|---|---|---|---|
| flaskbb/user/__init__.py | 0% | 0% | sem mudança |
| flaskbb/user/forms.py | 20% | 20% | sem mudança |
| flaskbb/user/models.py | 22% | 22% | sem mudança |
| flaskbb/user/plugins.py | 12% | 23% | +11 pontos percentuais |
| flaskbb/user/services/__init__.py | 100% | 100% | sem mudança |
| flaskbb/user/services/factories.py | 0% | 24% | +24 pontos percentuais |
| flaskbb/user/services/update.py | 36% | 36% | sem mudança |
| flaskbb/user/services/validators.py | 48% | 48% | sem mudança |
| flaskbb/user/views.py | 59% | 59% | sem mudança |
| **Total do módulo flaskbb/user** | **31%** | **33%** | **+2 pontos percentuais** |

A meta definida na Tarefa 1.2 (`parte1/PLANO_TESTES.md`) era de +15 pontos percentuais, saindo de 31% para pelo menos 46%. Essa meta **não foi atingida**, o resultado final ficou em 33%.

## 4. Por que a meta não foi atingida

Os testes novos desta Parte 1 (Tarefas 1.3, 1.4 e 1.5) concentraram-se, de propósito, em dois arquivos que estavam completamente sem testes próprios antes deste projeto, `flaskbb/user/plugins.py` e `flaskbb/user/services/factories.py`. Nesses dois arquivos específicos, o ganho de cobertura foi expressivo, de 12% para 23% no primeiro, e de 0% para 24% no segundo.

O problema é que, juntos, esses dois arquivos somam apenas 59 das 560 linhas de código do módulo inteiro, cerca de 10,5%. Mesmo dobrando a cobertura deles, o efeito no percentual total do módulo é pequeno. Os outros arquivos, principalmente os maiores, `flaskbb/user/models.py` (246 linhas) e `flaskbb/user/views.py` (124 linhas), não receberam nenhum teste novo nesta etapa, então continuam com a mesma cobertura da baseline.

O teste parametrizado da Tarefa 1.4, sobre `CantShareEmailValidator`, também não mudou o percentual de `services/validators.py`, porque ele exercita esse validador com dados de entrada diferentes, mas passando pelas mesmas linhas de código que os testes já existentes (`tests/unit/user/test_update_validator.py`) já cobriam desde a baseline. Isso não invalida o teste, ele aumenta a confiança sobre o comportamento do validador com mais combinações de entrada, só não aumenta a métrica de cobertura de linha, que só conta linhas novas executadas.

Em retrospecto, para atingir uma meta de +15 pontos percentuais no módulo inteiro, seria necessário também escrever testes para os arquivos maiores, especialmente `models.py` e `views.py`, o que ficou fora do escopo do número mínimo de casos exigido nesta etapa (8 casos, mais 1 parametrizado, mais 1 com mock).

## 5. Cenários que continuam descobertos, e sugestões para o futuro

- `flaskbb/user/plugins.py`, as funções `flaskbb_tpl_profile_settings_menu` e `flaskbb_tpl_profile_links` continuam sem teste. Elas usam o protocolo de "hookwrapper" do pluggy (geradores com `yield`), mais complexas de testar isoladamente. Sugestão, escrever um teste de integração real, registrando uma implementação de hook falsa no `plugin_manager` (fixture já existente no projeto) e conferindo o resultado final da lista combinada.
- `flaskbb/user/services/factories.py`, as funções `change_password_form_factory` e `change_details_form_factory` continuam sem teste direto, só `change_email_form_factory` foi testada na Tarefa 1.3. Sugestão, seguir exatamente o mesmo padrão já usado para `change_email_form_factory`, com `login_user` dentro de um `post_request_context`.
- `flaskbb/user/services/factories.py`, a função `settings_form_factory` também continua sem teste, ela tem dois caminhos possíveis, formulário ainda não submetido e formulário já submetido e validado. Sugestão, dois testes novos, um para cada caminho, usando `post_request_context` com dados de formulário simulados.
- `flaskbb/user/models.py`, o modelo `User` continua com pouca cobertura própria (22%), fora dos testes indiretos feitos através dos handlers. Sugestão, testes diretos para métodos como `check_password`, propriedades de permissão e o método `save`, sem depender das camadas de serviço.
- `flaskbb/user/views.py`, as classes de view continuam parcialmente cobertas (59%), principalmente pelos testes de `test_controllers.py` já existentes. Sugestão, casos de borda adicionais, como respostas de erro inesperadas do banco de dados, ou parâmetros de URL malformados.

## 6. Conclusão

O módulo `flaskbb/user` termina a Parte 1 com 33% de cobertura de linhas, um avanço real de 2 pontos percentuais em relação à baseline, concentrado em dois arquivos que antes não tinham nenhum teste. A meta de 46% definida na Tarefa 1.2 foi otimista para o escopo desta etapa, e fica registrada aqui, com honestidade, como não atingida, junto com sugestões concretas de como continuar fechando essa lacuna nas próximas iterações do projeto.