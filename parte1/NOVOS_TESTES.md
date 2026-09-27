# Parte 1, Tarefa 1.3, Novos Testes Unitários

Autor, João Ricardo Magalhães Oliveira
Disciplina, Engenharia de Software II
Data, 26/09/2026

## 1. Resumo

Foram adicionados 8 casos de teste novos, distribuídos em dois arquivos, ambos dentro do módulo escolhido na Tarefa 1.2, `flaskbb/user`. Depois da adição, a suíte completa passou de 233 para 241 testes, mantendo a mesma falha pré-existente de tradução registrada em `parte1/BASELINE.md`, sem nenhuma regressão.

## 2. Lista de casos

| # | Arquivo | Linhas | Tipo | Teste |
|---|---|---|---|---|
| 1 | tests/unit/user/test_plugins.py | 29-37 | Caminho feliz | test_gather_password_validators_returns_expected_validators |
| 2 | tests/unit/user/test_plugins.py | 41-51 | Caminho feliz | test_gather_email_validators_returns_expected_validators |
| 3 | tests/unit/user/test_plugins.py | 55-60 | Caminho feliz | test_gather_details_update_validators_returns_expected_validator |
| 4 | tests/unit/user/test_factories.py | 36-44 | Caminho feliz | test_settings_update_handler_returns_configured_handler |
| 5 | tests/unit/user/test_factories.py | 48-55 | Borda | test_details_update_factory_gathers_real_validator_from_hook |
| 6 | tests/unit/user/test_factories.py | 59-68 | Borda | test_password_update_handler_gathers_real_validators_from_hook |
| 7 | tests/unit/user/test_factories.py | 72-81 | Borda | test_email_update_handler_gathers_real_validators_from_hook |
| 8 | tests/unit/user/test_factories.py | 85-98 | Caminho feliz | test_change_email_form_factory_binds_current_user |

## 3. Observação

Os testes 5, 6 e 7 são classificados como borda porque não testam apenas o retorno de uma função isolada, e sim a integração real entre as fábricas de `flaskbb/user/services/factories.py` e os hooks de `flaskbb/user/plugins.py`, via o gerenciador de plugins, `pluggy`, do próprio projeto, algo que nenhum teste existente cobria antes desta tarefa.

Os testes com dublê (mock) e o teste parametrizado ficam para as Tarefas 1.4 e 1.5, e ainda vão referenciar alguns desses mesmos arquivos.

## 4. Teste parametrizado (Tarefa 1.4)

| Arquivo | Linhas | Tipo | Teste |
|---|---|---|---|
| tests/unit/user/test_email_validator_parametrized.py | 29-65 | Parametrizado, misturando caminho feliz e erro | test_cant_share_email_validator_com_varias_entradas |

Este teste cobre 4 combinações de entrada para o `CantShareEmailValidator`, duas que devem levantar `ValidationError` (email já cadastrado, com a mesma caixa e com caixa diferente) e duas que não devem (email sem conflito, e o próprio email atual do usuário). Durante a escrita deste teste, uma hipótese inicial sobre um possível problema de sensibilidade a maiúsculas/minúsculas no validador se mostrou incorreta, o teste revelou que a classe `EmailUpdate` (`flaskbb/core/user/update.py`) já normaliza ambos os emails para minúsculas antes de chegar no validador, então o comportamento está correto.


## 5. Teste com dublê / mock (Tarefa 1.5)

| Arquivo | Linhas | Tipo | Teste |
|---|---|---|---|
| tests/unit/user/test_password_update_handler_mock.py | 21-47 | Mock, isolando dependência externa | test_password_update_handler_aciona_o_hook_uma_vez |

O dublê substitui inteiramente o objeto `pluggy` (o gerenciador de plugins) usado dentro de `flaskbb/user/services/factories.py`, porque essa função acessa esse objeto diretamente do módulo, sem recebê-lo como parâmetro. O teste verifica interação com o dublê, conferindo que o hook `flaskbb_gather_password_validators` foi chamado exatamente uma vez, com o argumento `app` correto, e não apenas o resultado final. O banco de dados (`db`) permanece real, sem substituição, para manter o teste focado só na dependência que precisava ser isolada.