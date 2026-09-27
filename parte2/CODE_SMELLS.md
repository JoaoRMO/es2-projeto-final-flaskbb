# Catálogo de Code Smells, Parte 2

**Autor:** João Ricardo Magalhães Oliveira

**Arquivo de hotspot escolhido:** `flaskbb/user/models.py`

**Justificativa da escolha do arquivo:** o arquivo tem 528 linhas e reúne três
classes, `Group`, `User` e `Guest`, dentro do módulo `flaskbb/user`, que já foi
o módulo trabalhado na Parte 1. Isso significa que já existe uma suíte de
testes rodando por perto, incluindo os testes novos escritos na Parte 1, o que
dá mais segurança para refatorar sem quebrar comportamento. Na leitura do
arquivo, encontrei seis smells reais, sem precisar forçar nada, cobrindo
quatro categorias diferentes do catálogo de Fowler.

---

## Smell 1, Duplicated Code (get_permissions repetido entre User e Guest)

**Localização:** `flaskbb/user/models.py:394-408` (classe `User`) e
`flaskbb/user/models.py:508-522` (classe `Guest`)

```python
# User.get_permissions, linhas 394 a 408
@cache.memoize()
def get_permissions(self, exclude: set[str] | None = None):
    """Returns a dictionary with all permissions the user has"""
    if exclude:
        exclude = set(exclude)
    else:
        exclude = set()
    exclude.update(["id", "name", "description"])

    perms: dict[str, bool] = {}
    # Get the Guest group
    for group in self.groups:
        columns = set(group.__table__.columns.keys()) - set(exclude)
        for c in columns:
            perms[c] = getattr(group, c) or perms.get(c, False)
    return perms
```

```python
# Guest.get_permissions, linhas 508 a 522
@cache.memoize()
def get_permissions(self, exclude: set[str] | None = None):
    """Returns a dictionary with all permissions the user has"""
    if exclude:
        exclude = set(exclude)
    else:
        exclude = set()
    exclude.update(["id", "name", "description"])

    perms: dict[str, bool] = {}
    # Get the Guest group
    for group in self.groups:
        columns = set(group.__table__.columns.keys()) - set(exclude)
        for c in columns:
            perms[c] = getattr(group, c) or perms.get(c, False)
    return perms
```

**Por que é um smell:** as duas versões são idênticas linha por linha,
incluindo o comentário `# Get the Guest group`, que só faz sentido dentro da
classe `Guest`, e mesmo assim foi copiado para dentro de `User`. Esse detalhe
prova que o código foi copiado e colado, e não que as duas classes chegaram a
uma solução parecida por coincidência. Se um dia for preciso mudar a regra de
como as permissões são calculadas, por exemplo para tratar um novo tipo de
grupo, existe o risco real de alguém alterar só uma das duas cópias e deixar
a outra desatualizada, gerando um bug difícil de perceber.

---

## Smell 2, Duplicated Code (all_topics e all_posts quase idênticos)

**Localização:** `flaskbb/user/models.py:291-311` (`all_topics`) e
`flaskbb/user/models.py:313-331` (`all_posts`)

```python
# all_topics, linhas 291 a 311
def all_topics(self, page: int, viewer: "User"):
    group_ids = [g.id for g in viewer.groups]
    stmt = (
        db.select(Topic)
        .where(
            Topic.user_id == self.id,
            Forum.groups.any(Group.id.in_(group_ids)),
        )
        .order_by(Topic.id.desc())
    )
    topics = db.paginate(
        stmt, page=page, per_page=flaskbb_config["TOPICS_PER_PAGE"]
    )
    return topics

# all_posts, linhas 313 a 331
def all_posts(self, page: int, viewer: "User"):
    group_ids = [g.id for g in viewer.groups]
    stmt = (
        db.select(Post)
        .where(
            Post.user_id == self.id,
            Forum.groups.any(Group.id.in_(group_ids)),
        )
        .order_by(Post.id.desc())
    )
    posts = db.paginate(stmt, page=page, per_page=flaskbb_config["TOPICS_PER_PAGE"])
    return posts
```

**Por que é um smell:** a estrutura das duas funções é igual, muda só o
modelo consultado, `Topic` ou `Post`. E tem uma prova concreta de que a
duplicação já causou um problema, o `all_posts` usa
`flaskbb_config["TOPICS_PER_PAGE"]` para paginar posts, quando deveria existir
uma chave própria para posts. Isso é o retrato exato do risco clássico do
código duplicado, quem copiou e colou o método esqueceu de trocar esse
detalhe, e ninguém percebeu porque o teste que existe cobre só o caminho
feliz, não o valor exato da paginação.

---

## Smell 3, Duplicated Code (ban e unban espelhados)

**Localização:** `flaskbb/user/models.py:415-429` (`ban`) e
`flaskbb/user/models.py:431-451` (`unban`)

```python
# ban, linhas 415 a 429
def ban(self):
    """Bans the user. Returns True upon success."""
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

# unban, linhas 431 a 451
def unban(self):
    """Unbans the user. Returns True upon success."""
    if self.get_permissions()["banned"]:
        member_group = db.session.execute(
            db.select(Group).filter(
                Group.admin.is_(False),
                Group.super_mod.is_(False),
                Group.mod.is_(False),
                Group.guest.is_(False),
                Group.banned.is_(False),
            )
        ).scalar_one_or_none()

        if not member_group:
            abort(404)

        self.primary_group = member_group
        self.save()
        self.invalidate_cache()
        return True
    return False
```

**Por que é um smell:** os dois métodos seguem exatamente o mesmo roteiro,
checa uma condição, busca um grupo, aborta com 404 se não achar, troca o
grupo primário, salva, invalida o cache, retorna `True` ou `False`. Só muda a
condição de entrada e o filtro usado na busca do grupo. Esse tipo de espelho
quase perfeito é um convite a extrair um método comum que recebe só o filtro
e a condição como parâmetro.

---

## Smell 4, Primitive Obsession (permissões como dict de string para bool)

**Localização:** `flaskbb/user/models.py:402` e `flaskbb/user/models.py:415`
(entre outros pontos que leem `get_permissions()["banned"]`)

```python
# trecho de get_permissions, linha 402
perms: dict[str, bool] = {}
...

# uso em ban, linha 417
if not self.get_permissions()["banned"]:
```

**Por que é um smell:** as permissões do usuário são representadas como um
dicionário solto de string para booleano, ao invés de um objeto de valor
próprio, algo como uma classe `Permissions` com atributos nomeados. Isso é
uma Obsessão por Tipos Primitivos, o nome da permissão vira uma string mágica
espalhada pelo código, `"banned"`, sem checagem do compilador ou do editor.
Se alguém digitar `"baned"` por engano em algum lugar novo, o programa não
avisa nada, simplesmente devolve `False` do jeito errado.

---

## Smell 5, Comentário sinalizando dívida técnica

**Localização:** `flaskbb/user/models.py:461-462`, dentro do método `save`

```python
# linhas 461 a 469
if groups is not None:
    # TODO: Only remove/add groups that are selected
    with db.session.no_autoflush:
        secondary_groups = (
            db.session.execute(self.secondary_groups.select()).scalars().all()
        )

        for group in secondary_groups:
            self.remove_from_group(group)
```

**Por que é um smell:** o comentário `TODO: Only remove/add groups that are
selected` é o próprio desenvolvedor original admitindo que a implementação
atual não é a ideal, ela remove todos os grupos secundários do usuário e
depois adiciona de novo só os que foram passados, ao invés de comparar as
duas listas e mexer só na diferença. Isso é dívida técnica documentada e
nunca paga, um comentário assim é um sinal de alerta de que existe um jeito
mais correto de fazer a mesma coisa, só que ele nunca foi implementado.

---

## Smell 6, Long Method com responsabilidades misturadas

**Localização:** `flaskbb/user/models.py:453-481`, método `save`

```python
# linhas 453 a 481
@override
def save(self, groups: list[Group] | None = None) -> "User":
    """Saves a user. If a list with groups is provided, it will add those
    to the secondary groups from the user.

    :param groups: A list with groups that should be added to the
                   secondary groups from user.
    """
    if groups is not None:
        # TODO: Only remove/add groups that are selected
        with db.session.no_autoflush:
            secondary_groups = (
                db.session.execute(self.secondary_groups.select()).scalars().all()
            )

            for group in secondary_groups:
                self.remove_from_group(group)

        for group in groups:
            # Do not add the primary group to the secondary groups
            if group == self.primary_group:
                continue
            self.add_to_group(group)

        self.invalidate_cache()

    db.session.add(self)
    db.session.commit()
    return self
```

**Por que é um smell:** o método `save` deveria, pelo nome, só persistir o
usuário no banco. Só que ele também decide qual estratégia usar para
recalcular os grupos secundários, remove todos, adiciona os novos, filtra o
grupo primário para não duplicar, e ainda invalida o cache. São várias
tarefas diferentes dentro de um único método, o que fere o princípio da
coesão, cada unidade de código deveria fazer uma única tarefa relacionada.
Isso torna o método mais difícil de ler, de testar isoladamente, e de
reaproveitar a lógica de atualização de grupos em outro lugar sem também
disparar um `commit` no banco.
