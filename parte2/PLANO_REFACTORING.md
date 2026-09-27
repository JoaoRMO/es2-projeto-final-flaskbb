# Plano de Refactoring, Parte 2

**Autor:** João Ricardo Magalhães Oliveira

Este plano trata 4 dos 6 smells registrados em `parte2/CODE_SMELLS.md`. Os
smells 2 e 5 do catálogo ficaram de fora desta parte, por motivos explicados
no final deste documento.

---

## Refatoração 1, smell 1 (Duplicated Code em get_permissions)

**Refatoração nomeada:** Extract Method

**O que vai ser feito:** a lógica que hoje está copiada dentro de
`User.get_permissions` e `Guest.get_permissions` vai ser extraída para uma
função só, no nível do módulo, algo como `_collect_permissions(groups,
exclude)`. As duas classes continuam com seus métodos `get_permissions`,
mas o corpo de cada um passa a só chamar essa função compartilhada.

**Resultado esperado:** existe uma única implementação da lógica de
permissões, usada tanto por `User` quanto por `Guest`, então uma mudança
futura na regra precisa ser feita em um único lugar.

**Riscos antecipados:** o decorador `@cache.memoize()` está em cada método,
não na função extraída, então preciso ter cuidado para o cache continuar
funcionando por instância, e não virar um cache global compartilhado entre
usuários diferentes. Também preciso confirmar que `self.groups` de `User` e
`self.groups` de `Guest` continuam sendo passados corretamente para a função
extraída.

---

## Refatoração 2, smell 3 (Duplicated Code em ban e unban)

**Refatoração nomeada:** Extract Method

**O que vai ser feito:** o trecho repetido, buscar um grupo com um filtro,
abortar com 404 se não encontrar, trocar o grupo primário, salvar e
invalidar o cache, vai virar um método interno, algo como
`_switch_primary_group(self, group_filter)`. Os métodos `ban` e `unban`
continuam com suas condições de entrada próprias, mas passam a chamar esse
método interno.

**Resultado esperado:** `ban` e `unban` ficam bem mais curtos, cada um só
verifica sua condição de entrada e delega o resto para o método
compartilhado.

**Riscos antecipados:** o `abort(404)` precisa continuar interrompendo a
execução do jeito certo dentro do método extraído, e o valor de retorno,
`True` ou `False`, precisa continuar batendo com o comportamento original em
todos os casos, inclusive quando o grupo não é encontrado.

---

## Refatoração 3, smell 6 (Long Method em save)

**Refatoração nomeada:** Extract Method

**O que vai ser feito:** a parte do método `save` que decide quais grupos
secundários remover e adicionar vai ser extraída para um método próprio,
algo como `_update_secondary_groups(self, groups)`. O método `save` original
passa a só chamar esse novo método, quando `groups` não é `None`, e depois
seguir com a persistência no banco.

**Resultado esperado:** `save` fica focado só em persistir o usuário no
banco, e a lógica de atualização de grupos secundários vira uma
responsabilidade separada, mais fácil de entender e de testar sozinha.

**Riscos antecipados:** a ordem das operações precisa continuar igual,
atualizar os grupos, invalidar o cache, e só depois adicionar e commitar a
sessão do banco. Se essa ordem mudar, algum teste que dependa do estado do
cache ou da sessão no momento certo pode quebrar.

---

## Refatoração 4, smell 4 (Primitive Obsession na string "banned")

**Refatoração nomeada:** Replace Magic Number with Symbolic Constant
(adaptada para string mágica)

**O que vai ser feito:** a string literal `"banned"`, usada como chave do
dicionário de permissões dentro de `ban` e `unban`, vai virar uma constante
nomeada no início do módulo, por exemplo `PERMISSAO_BANIDO = "banned"`. Os
dois métodos passam a usar essa constante ao invés da string solta.

**Resultado esperado:** o significado da string fica explícito pelo nome da
constante, e um erro de digitação nessa string agora só pode acontecer em um
lugar, na definição da constante, não em cada uso espalhado pelo código.

**Riscos antecipados:** é a refatoração de menor risco das quatro, mas
preciso conferir se essa mesma string `"banned"` aparece em outro lugar do
código, fora do arquivo alvo, como em testes que fazem
`get_permissions()["banned"]` diretamente, e trocar todos os usos juntos.

---

## Por que os smells 2 e 5 ficaram de fora

- **Smell 2** (`all_topics` e `all_posts` quase idênticos) esconde um bug de
  verdade, `all_posts` usa a config `TOPICS_PER_PAGE` ao invés de uma config
  própria para posts. Corrigir isso mudaria o comportamento observável do
  sistema, o que contraria a regra da Tarefa 2.3 de que nenhuma refatoração
  pode alterar comportamento testado pela suíte. Fica registrado como
  pendência, não como refatoração desta parte.
- **Smell 5** (comentário `TODO` dentro de `save`) vai ser tratado na Tarefa
  2.4, que já tem uma categoria própria para eliminação de comentário
  desatualizado.
