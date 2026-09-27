# Refatorações Aplicadas, Parte 2

**Autor:** João Ricardo Magalhães Oliveira

**Arquivo refatorado:** `flaskbb/user/models.py`

As 4 refatorações abaixo seguem exatamente o plano descrito em
`parte2/PLANO_REFACTORING.md`, aplicadas em 4 commits separados no fork do
flaskbb. Depois de cada commit, a suíte completa foi rodada com
`uv run pytest -n 0` (sem paralelismo, ver observação 1 no final deste
documento) e o resultado se manteve estável em `1 failed, 244 passed, 1
skipped`, o mesmo teste que já falhava desde a Parte 1
(`test_flaskbbdomain_translations`, problema de ambiente, sem relação com o
código do projeto).

---

## Commit `105ce87`

**Smell tratado:** Smell 1 do catálogo, Duplicated Code em `get_permissions`.

**Transformação aplicada:** Extract Method. A lógica que estava copiada dentro
de `User.get_permissions` e `Guest.get_permissions` foi extraída para uma
função de módulo, `_collect_permissions(groups, exclude)`.

**Antes:**
```python
# repetido, palavra por palavra, em User e em Guest
perms: dict[str, bool] = {}
for group in self.groups:
    columns = set(group.__table__.columns.keys()) - set(exclude)
    for c in columns:
        perms[c] = getattr(group, c) or perms.get(c, False)
return perms
```

**Depois:**
```python
# User.get_permissions e Guest.get_permissions, os dois iguais agora
@cache.memoize()
def get_permissions(self, exclude: set[str] | None = None):
    """Returns a dictionary with all permissions the user has"""
    return _collect_permissions(self.groups, exclude)
```

---

## Commit `fda1d4d`

**Smell tratado:** Smell 3 do catálogo, Duplicated Code em `ban` e `unban`.

**Transformação aplicada:** Extract Method. O trecho repetido, buscar um
grupo por um filtro, abortar com 404 se não encontrar, trocar o grupo
primário, salvar e invalidar o cache, virou o método
`_switch_primary_group(group_filter)`.

**Antes:**
```python
def ban(self):
    if not self.get_permissions()["banned"]:
        banned_group = db.session.execute(
            db.select(Group).filter(Group.banned.is_(True))
        ).scalar_one_or_none()
        if not banned_group:
            abort(404)
        self.primary_group = banned_group
        self.save()
        self.invalidate_cache()
        return True
    return False
```

**Depois:**
```python
def ban(self):
    if not self.get_permissions()["banned"]:
        self._switch_primary_group([Group.banned.is_(True)])
        return True
    return False
```

(`unban` seguiu o mesmo padrão, só muda o filtro passado para
`_switch_primary_group`.)

---

## Commit `0328355`

**Smell tratado:** Smell 6 do catálogo, Long Method com responsabilidades
misturadas em `save`.

**Transformação aplicada:** Extract Method. A parte de `save` que decide
quais grupos secundários remover e adicionar foi extraída para
`_update_secondary_groups(groups)`.

**Antes:**
```python
def save(self, groups=None):
    if groups is not None:
        # TODO: Only remove/add groups that are selected
        with db.session.no_autoflush:
            secondary_groups = (
                db.session.execute(self.secondary_groups.select()).scalars().all()
            )
            for group in secondary_groups:
                self.remove_from_group(group)
        for group in groups:
            if group == self.primary_group:
                continue
            self.add_to_group(group)
        self.invalidate_cache()
    db.session.add(self)
    db.session.commit()
    return self
```

**Depois:**
```python
def _update_secondary_groups(self, groups):
    # TODO: Only remove/add groups that are selected
    with db.session.no_autoflush:
        secondary_groups = (
            db.session.execute(self.secondary_groups.select()).scalars().all()
        )
        for group in secondary_groups:
            self.remove_from_group(group)
    for group in groups:
        if group == self.primary_group:
            continue
        self.add_to_group(group)
    self.invalidate_cache()

def save(self, groups=None):
    if groups is not None:
        self._update_secondary_groups(groups)
    db.session.add(self)
    db.session.commit()
    return self
```

O comentário `TODO` foi mantido de propósito, ele é o smell 5 do catálogo e
vai ser tratado separadamente na Tarefa 2.4.

---

## Commit `90d7906`

**Smell tratado:** Smell 4 do catálogo, Primitive Obsession na string
`"banned"`.

**Transformação aplicada:** Replace Magic Number with Symbolic Constant
(adaptada para string). A string `"banned"`, usada como chave do dicionário
de permissões, virou a constante `PERMISSAO_BANIDO`.

**Antes:**
```python
PERMISSAO_BANIDO não existia ainda

if not self.get_permissions()["banned"]:
    ...
if self.get_permissions()["banned"]:
    ...
```

**Depois:**
```python
PERMISSAO_BANIDO = "banned"

if not self.get_permissions()[PERMISSAO_BANIDO]:
    ...
if self.get_permissions()[PERMISSAO_BANIDO]:
    ...
```

---

## Observações

1. **Sobre a instabilidade encontrada na suíte em paralelo.** Durante a
   Refatoração 2, a suíte rodando em paralelo (`pytest-xdist`) apresentou
   falhas diferentes a cada execução, em testes sem nenhuma relação com o
   código alterado (um teste de validação de avatar, depois um teste de
   `forum_is_unread` com erro de configuração `None`). Rodando a suíte sem
   paralelismo (`uv run pytest -n 0`), o resultado ficou estável em `1
   failed, 244 passed, 1 skipped` em todas as execuções seguintes. Isso
   indica um problema pré-existente de isolamento entre testes quando
   rodam em paralelo, provavelmente estado global compartilhado entre
   workers, e não algo causado pelas refatorações desta parte.

2. **Sobre a cobertura dos métodos alterados.** Ao procurar por testes que
   chamam `ban()`, `unban()`, `get_permissions()` ou `save(groups=...)`
   diretamente, não foi encontrado nenhum na suíte atual. Isso significa
   que a suíte verde comprova que nada mais no sistema quebrou, mas não é
   uma prova direta e específica de que o comportamento desses quatro
   métodos continua idêntico em todos os casos. Fica registrado como uma
   limitação conhecida, não como algo resolvido nesta parte.
