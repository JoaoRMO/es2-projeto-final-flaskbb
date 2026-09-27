# Melhorias de Legibilidade, Parte 2

**Autor:** João Ricardo Magalhães Oliveira

**Arquivo:** `flaskbb/user/models.py`

As 3 melhorias abaixo foram aplicadas em commits separados, cada uma de uma
categoria diferente, seguindo o que pede a Tarefa 2.4. Depois de cada
commit, a suíte foi rodada com `uv run pytest -n 0` e se manteve estável em
`1 failed, 244 passed, 1 skipped`, o mesmo falho conhecido desde a Parte 1.

---

## Melhoria 1, categoria Comentários

**Commit:** `42d89a3`

**O que mudou:** o comentário `# TODO: Only remove/add groups that are
selected`, dentro de `_update_secondary_groups`, foi removido e substituído
por uma docstring explicando a estratégia atual do método.

**Antes:**
```python
def _update_secondary_groups(self, groups: list[Group]) -> None:
    """Atualiza os grupos secundarios do usuario para a lista informada."""
    # TODO: Only remove/add groups that are selected
    with db.session.no_autoflush:
        ...
```

**Depois:**
```python
def _update_secondary_groups(self, groups: list[Group]) -> None:
    """Atualiza os grupos secundarios do usuario para a lista informada.

    A estrategia atual remove todos os grupos secundarios existentes e
    adiciona de volta apenas os grupos informados. Isso e mais simples
    de entender do que calcular a diferenca entre as duas listas, ao
    custo de fazer mais operacoes de banco do que o estritamente
    necessario.
    """
    with db.session.no_autoflush:
        ...
```

**Justificativa:** um comentário `TODO` sem responsável e sem prazo é dívida
técnica que nunca é paga, ele só fica ali sinalizando um problema que
ninguém vai resolver. Trocar isso por uma explicação honesta do porquê da
escolha atual é mais útil para quem lê o código depois, e não promete um
conserto que não vai acontecer nesta parte do projeto.

---

## Melhoria 2, categoria Nomenclatura

**Commit:** `49e4cd2`

**O que mudou:** a constante `PERMISSAO_BANIDO`, criada na Tarefa 2.3, foi
renomeada para `BANNED_PERMISSION_KEY`.

**Antes:**
```python
PERMISSAO_BANIDO = "banned"
...
if not self.get_permissions()[PERMISSAO_BANIDO]:
```

**Depois:**
```python
BANNED_PERMISSION_KEY = "banned"
...
if not self.get_permissions()[BANNED_PERMISSION_KEY]:
```

**Justificativa:** todo o restante do arquivo `models.py`, e do projeto
flaskbb como um todo, usa nomes em inglês, `get_permissions`,
`remove_from_group`, `invalidate_cache`. Uma constante em português quebrava
essa consistência, a linguagem ubíqua já estabelecida no código. Renomear
para inglês alinha o nome novo com o padrão que já existia antes da nossa
refatoração.

---

## Melhoria 3, categoria Estilo de código

**Commit:** `eeafa22`

**O que mudou:** parênteses redundantes ao redor da divisão, dentro das
propriedades `posts_per_day` e `topics_per_day`, foram removidos.

**Antes:**
```python
@property
def posts_per_day(self):
    """Returns the posts per day count."""
    return round((float(self.post_count) / float(self.days_registered)), 1)
```

**Depois:**
```python
@property
def posts_per_day(self):
    """Returns the posts per day count."""
    return round(float(self.post_count) / float(self.days_registered), 1)
```

**Justificativa:** os parênteses extras não mudavam a ordem das operações,
a divisão já era calculada antes do `round` de qualquer jeito, com ou sem
eles. Eram só ruído visual na expressão, sem nenhum efeito no resultado.
Tirar esse excesso deixa a linha mais direta de ler.
