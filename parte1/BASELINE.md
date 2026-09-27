# Parte 1, Tarefa 1.1, Baseline do Projeto

Autor, João Ricardo Magalhães Oliveira
Disciplina, Engenharia de Software II
Data, 26/09/2026

## 1. Objetivo deste documento

Este documento registra o estado inicial do projeto, antes de qualquer alteração de código, servindo como ponto de partida para comparação com os resultados finais da Parte 1.

## 2. Ambiente utilizado

- Commit base do fork, `5309b1b`, correspondente ao código recebido do fork do professor `jeffsantos/flaskbb`, sem nenhuma modificação.
- Gerenciador de ambiente, `uv`, versão `0.12.19`.
- Python, versão `3.13.7`.
- Framework de testes, `pytest`, versão `9.0.3`, com os plugins `pytest-mock`, `pytest-cov` e `pytest-xdist`.
- Comando usado para instalar as dependências, `uv sync`.

## 3. Resultado da suíte de testes existente

Comando executado, `uv run pytest`.

Resultado, 232 testes aprovados e 1 teste reprovado, em um total de 233 testes, rodando em 10 processos paralelos (`pytest-xdist`), com 6 avisos (warnings).

### 3.1 Teste reprovado

`tests/unit/utils/test_translations.py::test_flaskbbdomain_translations`

Esse teste espera que o objeto de domínio de tradução do FlaskBB retorne uma instância da classe `Translations`, da biblioteca Babel, mas no ambiente usado ele retornou uma instância de `NullTranslations`, que representa a ausência de traduções carregadas.

Essa falha já existia no código recebido do fork, antes de qualquer alteração feita para este projeto, portanto não é consequência de nenhuma mudança realizada até este ponto. O motivo mais provável é a falta dos arquivos de tradução compilados, arquivos `.mo`, que normalmente são gerados por um passo separado de build e não fazem parte do repositório versionado. Esse comportamento está sendo apenas registrado aqui como parte do estado inicial, não sendo objetivo desta parte do projeto corrigir esse teste.

### 3.2 Informações para contato com o professor

Conforme pedido no guia-setup-ambiente.md, seção 5, seguem os detalhes técnicos deste ambiente, para relato ao professor.

- Sistema operacional, macOS (Darwin), Apple Silicon (M4).
- Versão do Python, 3.13.7.
- Versão do uv, 0.12.19.
- Versão do pytest, 9.0.3, com os plugins pytest-mock 3.15.1, pytest-cov 7.1.0 e pytest-xdist 3.8.0.
- Mensagem de erro completa.

```
tests/unit/utils/test_translations.py:9: in test_flaskbbdomain_translations
    assert isinstance(domain.get_translations(), Translations)
E   assert False
E    +  where False = isinstance(<babel.support.NullTranslations object at 0x10afc1490>, Translations)
E    +    where <babel.support.NullTranslations object at 0x10afc1490> = get_translations()
E    +      where get_translations = <flaskbb.utils.translations.FlaskBBDomain object at 0x10acd78c0>.get_translations
```

## 4. Cobertura de código, baseline

Comando executado.

uv run pytest --cov=flaskbb.user --cov=flaskbb.forum --cov=flaskbb.management --cov-report=term-missing


Esse comando mede quais linhas de código dos módulos `flaskbb/user`, `flaskbb/forum` e `flaskbb/management` foram executadas durante a suíte de testes existente.

### 4.1 Cobertura por módulo

| Módulo | Linhas de código (Stmts) | Linhas não cobertas (Miss) | Cobertura |
|---|---|---|---|
| flaskbb/forum | 1272 | 854 | 33% |
| flaskbb/management | 837 | 774 | 8% |
| flaskbb/user | 560 | 388 | 31% |
| Total dos três módulos | 2669 | 2016 | 24% |

### 4.2 Cobertura por arquivo

| Arquivo | Stmts | Miss | Cover |
|---|---|---|---|
| flaskbb/forum/init.py | 2 | 2 | 0% |
| flaskbb/forum/forms.py | 91 | 91 | 0% |
| flaskbb/forum/locals.py | 29 | 18 | 38% |
| flaskbb/forum/models.py | 641 | 271 | 58% |
| flaskbb/forum/utils.py | 10 | 7 | 30% |
| flaskbb/forum/views.py | 499 | 465 | 7% |
| flaskbb/management/init.py | 4 | 4 | 0% |
| flaskbb/management/forms.py | 208 | 208 | 0% |
| flaskbb/management/models.py | 66 | 50 | 24% |
| flaskbb/management/plugins.py | 16 | 10 | 38% |
| flaskbb/management/views.py | 543 | 502 | 8% |
| flaskbb/user/init.py | 4 | 4 | 0% |
| flaskbb/user/forms.py | 45 | 36 | 20% |
| flaskbb/user/models.py | 246 | 193 | 22% |
| flaskbb/user/plugins.py | 26 | 23 | 12% |
| flaskbb/user/services/init.py | 0 | 0 | 100% |
| flaskbb/user/services/factories.py | 33 | 33 | 0% |
| flaskbb/user/services/update.py | 42 | 27 | 36% |
| flaskbb/user/services/validators.py | 40 | 21 | 48% |
| flaskbb/user/views.py | 124 | 51 | 59% |

## 5. Observações para as próximas tarefas

O módulo `flaskbb/user` foi escolhido como foco principal de testes novos na Parte 1, justificativa detalhada será registrada em `PLANO_TESTES.md`. Dentro dele, os arquivos com menor cobertura hoje são `flaskbb/user/services/factories.py`, com 0%, `flaskbb/user/plugins.py`, com 12%, e `flaskbb/user/forms.py`, com 20%, sendo bons candidatos para os novos casos de teste.