# -*- coding: utf-8 -*-
"""
Teste parametrizado da Tarefa 1.4, para o modulo
flaskbb.user.services.validators.

Este teste verifica quatro combinacoes de entrada para o
CantShareEmailValidator. A principio eu esperava que letras maiusculas
no novo email pudessem enganar o validador, ja que a consulta no banco
so coloca o email ja cadastrado em minusculas, com func.lower, sem
fazer o mesmo com o novo email recebido. Rodando o teste, descobri que
isso nao acontece, porque a classe EmailUpdate, em
flaskbb/core/user/update.py, ja converte tanto o email antigo quanto o
novo para minusculas assim que o objeto e criado, antes mesmo de
chegar no validador. Os quatro casos abaixo ficam registrados assim
mesmo, para deixar esse comportamento documentado, com duas entradas
que devem gerar erro e duas que nao devem.
"""

import pytest

from flaskbb.core.exceptions import ValidationError
from flaskbb.core.user.update import EmailUpdate
from flaskbb.user.models import User
from flaskbb.user.services.validators import CantShareEmailValidator

pytestmark = pytest.mark.usefixtures("default_settings")


@pytest.mark.parametrize(
    "new_email, deve_levantar_erro",
    [
        pytest.param(
            "test_normal@example.org",
            True,
            id="email_ja_cadastrado_mesma_caixa",
        ),
        pytest.param(
            "TEST_NORMAL@EXAMPLE.ORG",
            True,
            id="email_ja_cadastrado_caixa_diferente_normalizado_pelo_changeset",
        ),
        pytest.param(
            "email-totalmente-novo@example.org",
            False,
            id="email_sem_nenhum_conflito",
        ),
        pytest.param(
            "fred@fred.fred",
            False,
            id="proprio_email_atual_do_usuario_nao_conta_como_conflito",
        ),
    ],
)
def test_cant_share_email_validator_com_varias_entradas(
    new_email, deve_levantar_erro, user, Fred
):
    change = EmailUpdate(Fred.email, new_email)

    if deve_levantar_erro:
        with pytest.raises(ValidationError):
            CantShareEmailValidator(User).validate(Fred, change)
    else:
        # Se levantar excecao aqui, o teste ja falha sozinho, nao
        # precisa de asserção extra.
        CantShareEmailValidator(User).validate(Fred, change)