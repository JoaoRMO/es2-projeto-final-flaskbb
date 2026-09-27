# Parte 1, Tarefa 1.2, Escolha do Módulo Alvo e Meta de Cobertura

Autor, João Ricardo Magalhães Oliveira
Disciplina, Engenharia de Software II
Data, 26/09/2026

## 1. Módulo escolhido

`flaskbb/user`

## 2. Justificativa

O módulo `flaskbb/user` foi escolhido por quatro motivos.

Primeiro, tamanho gerenciável, 560 linhas de código, contra 1272 de `flaskbb/forum` e 837 de `flaskbb/management`, o que permite um avanço real de cobertura dentro do número de casos exigido nesta etapa do projeto.

Segundo, boa parte da lógica de negócio do módulo está isolada em funções e classes puras, dentro de `services/validators.py`, `services/update.py` e `services/factories.py`, que não dependem fortemente do banco de dados nem do ciclo completo de requisição HTTP, o que facilita escrever testes unitários rápidos e isolados.

Terceiro, é um módulo sensível do ponto de vista de segurança, pois trata troca de senha, troca de e-mail e alteração de dados pessoais do usuário, áreas em que falhas de validação têm maior impacto para quem usa o sistema.

Quarto, o módulo já conta com uma suíte de testes existente relativamente estruturada, o que dá um padrão de fixtures e estilo de asserção para seguir ao escrever os novos casos, reduzindo o risco de inconsistência.

## 3. Cobertura atual do módulo

Medida na Tarefa 1.1, com o comando `uv run pytest --cov=flaskbb.user --cov-report=term-missing`.

Cobertura de linhas, 31%, ou seja, 172 de 560 linhas executadas pelos testes existentes.

Observação, esta medição cobre apenas linhas, não ramos (branches). Se for necessário também medir cobertura de branches, o comando muda para `uv run pytest --cov=flaskbb.user --cov-branch --cov-report=term-missing`, isso pode ser feito antes do relatório final da Tarefa 1.6, caso o professor peça essa granularidade.

## 4. Meta concreta de incremento

Aumentar a cobertura de linhas do módulo `flaskbb/user` em pelo menos 15 pontos percentuais, saindo de 31% para 46% ou mais, até o fim da Parte 1.

Dentro dessa meta geral, dois alvos específicos.

- Levar `flaskbb/user/services/factories.py`, hoje em 0%, para pelo menos 70%.
- Levar `flaskbb/user/plugins.py`, hoje em 12%, para pelo menos 60%.

## 5. Cenários ainda não cobertos, a atacar nas próximas tarefas

1. Caminho feliz, `flaskbb_gather_password_validators()` retorna uma lista contendo instâncias de `OldPasswordMustMatch` e `PasswordsMustBeDifferent`, na ordem esperada (`flaskbb/user/plugins.py`).
2. Caminho feliz, `flaskbb_gather_email_validators()` retorna uma lista contendo `OldEmailMustMatch`, `EmailsMustBeDifferent` e `CantShareEmailValidator`, este último corretamente inicializado com o modelo `User` (`flaskbb/user/plugins.py`).
3. Caminho feliz, `flaskbb_gather_details_update_validators()` retorna uma lista contendo uma instância de `ValidateAvatarURL` (`flaskbb/user/plugins.py`).
4. Caminho feliz, com dublê, `password_update_handler()` aciona o hook do pluggy `flaskbb_gather_password_validators` e monta um `DefaultPasswordUpdateHandler` com os validadores retornados por esse hook (`flaskbb/user/services/factories.py`, candidato natural para o teste com mock da Tarefa 1.5).
5. Caminho feliz, `settings_update_handler()` retorna uma instância de `DefaultSettingsUpdateHandler`, configurada com os objetos `db` e `plugin_manager` corretos (`flaskbb/user/services/factories.py`).
6. Borda, `change_password_form_factory()` e `change_email_form_factory()` constroem os formulários corretamente vinculados ao usuário atual, mesmo quando esse usuário não tem dados extras preenchidos (`flaskbb/user/services/factories.py`).
7. Borda, `GeneralSettingsForm.as_change()` retorna os dados corretos de tema e idioma, tanto quando o formulário ainda não foi submetido, usando os valores atuais do usuário, quanto quando já foi submetido e validado, usando os valores enviados (`flaskbb/user/services/factories.py`, função `settings_form_factory`).
8. Borda, `ChangeUserDetailsForm.validate_birthday()` aceita corretamente o campo de aniversário vazio, sem lançar erro de validação, cobrindo o caminho de borda desse validador customizado (`flaskbb/user/forms.py`).