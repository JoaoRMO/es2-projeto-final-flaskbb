# Parte 3, Tarefa 3.1, Documentação Estratégica do Módulo

**Autor:** João Ricardo Magalhães Oliveira

**Módulo documentado:** `flaskbb/user`

## 1. Propósito do módulo

O módulo `flaskbb/user` é responsável por tudo que envolve a conta de um
usuário já registrado no fórum, o modelo de dados do usuário e do grupo de
permissões que ele pertence, a tela de perfil público e as telas de
configurações pessoais, troca de senha, troca de email e troca de detalhes
do perfil. Ele não cuida de cadastro ou login, isso fica em `flaskbb/auth`,
o `user` entra em cena depois que a pessoa já está autenticada e quer ver ou
mudar algo sobre a própria conta.

## 2. Mapa dos arquivos principais

| Arquivo | Responsabilidade |
|---|---|
| `flaskbb/user/__init__.py` | Garante que os hooks deste módulo sejam registrados na inicialização do FlaskBB, importando `plugins` mesmo sem usá-lo diretamente. |
| `flaskbb/user/models.py` | Modelos ORM `Group`, `User` e `Guest`, persistência de contas, grupos e cálculo de permissões. |
| `flaskbb/user/views.py` | Views HTTP do perfil e das telas de configuração, e registro das rotas do blueprint `user`. |
| `flaskbb/user/forms.py` | Formulários WTForms usados pelas views, convertendo dados de formulário em objetos de changeset. |
| `flaskbb/user/plugins.py` | Implementações de hooks do `pluggy`, menu e links de navegação do perfil, e pontos de extensão para coleta de validadores. |
| `flaskbb/user/services/factories.py` | Funções fábrica que montam formulários e handlers, conectando o `pluggy` aos serviços de atualização. |
| `flaskbb/user/services/update.py` | Handlers que aplicam changesets validados, persistem a mudança no banco e disparam hooks de pós-atualização. |
| `flaskbb/user/services/validators.py` | Validadores de regras de negócio para troca de senha, email e detalhes do usuário. |

## 3. Pontos de entrada externos

**Rotas HTTP**, registradas pelo hook `flaskbb_load_blueprints` em
`views.py`, todas sob o blueprint `user`:

| Rota | View | Método |
|---|---|---|
| `/settings/general` | `UserSettings` | GET, POST |
| `/settings/password` | `ChangePassword` | GET, POST |
| `/settings/email` | `ChangeEmail` | GET, POST |
| `/settings/user-details` | `ChangeUserDetails` | GET, POST |
| `/<username>` | `UserProfile` | GET |
| `/<username>/topics` | `AllUserTopics` | GET |
| `/<username>/posts` | `AllUserPosts` | GET |

**Pontos de extensão do `pluggy`** (outros plugins podem se conectar aqui):

- `flaskbb_gather_password_validators`, `flaskbb_gather_email_validators`,
  `flaskbb_gather_details_update_validators`, em `plugins.py`, permitem que
  outro plugin adicione seus próprios validadores às trocas de senha, email
  e detalhes.
- `flaskbb_tpl_profile_settings_menu` e `flaskbb_tpl_profile_links`, em
  `plugins.py`, permitem que outro plugin adicione itens ao menu de
  configurações e links de navegação do perfil.

## 4. Destinos de saída

- **Persistência no banco de dados**, via SQLAlchemy, nas tabelas `users`,
  `groups` e `groups_users` (modelos `User` e `Group`, em `models.py`).
- **Hooks de pós-atualização do `pluggy`**, disparados depois de cada
  mudança persistida com sucesso, `flaskbb_details_updated`,
  `flaskbb_password_updated`, `flaskbb_email_updated` e
  `flaskbb_settings_updated` (todos em `services/update.py`). Esses hooks
  podem ser consumidos por outros módulos ou plugins, por exemplo para
  disparar notificações.
- **Requisição HTTP de saída**, dentro de `ValidateAvatarURL.validate`
  (`services/validators.py:98-107`), que busca a imagem na URL de avatar
  informada pelo usuário, para checar suas dimensões antes de aceitar a
  mudança.

## 5. Docstrings novas ou reescritas

Seis docstrings foram adicionadas em pontos onde o nome da função sozinho
não era suficiente para entender o contrato, todas commitadas no fork do
flaskbb (commits `a70abb6` e `d387b69`).

| Local | Por que não era óbvio |
|---|---|
| `flaskbb/user/plugins.py:50-60`, `flaskbb_tpl_profile_links` | Usa o protocolo de hookwrapper do pluggy (`yield` + `outcome.force_result`), que não se explica sozinho para quem não conhece o pluggy. |
| `flaskbb/user/plugins.py:86-96`, `flaskbb_gather_password_validators` | O nome sugere só "buscar validadores", mas na verdade é um ponto de extensão, outros plugins podem implementar o mesmo hook para adicionar mais validadores. |
| `flaskbb/user/plugins.py:100-107`, `flaskbb_gather_email_validators` | Mesmo caso do anterior, para o fluxo de email. |
| `flaskbb/user/plugins.py:111-117`, `flaskbb_gather_details_update_validators` | Mesmo caso, para o fluxo de detalhes do perfil. |
| `flaskbb/user/services/validators.py:30-44`, `CantShareEmailValidator.validate` | A consulta só aplica `func.lower()` do lado do banco, e não do lado de `changeset.new_email`. Isso só funciona porque `EmailUpdate` já normaliza o email para minúsculas antes de chegar aqui, uma dependência entre dois arquivos diferentes que não é visível olhando só para esta função (descoberta durante a Parte 1, na Tarefa 1.4). |
| `flaskbb/user/forms.py:118-130`, `validate_birthday` | O nome sugere uma validação de verdade, mas o método hoje é um no-op, não levanta nenhum erro em nenhum caso. |
