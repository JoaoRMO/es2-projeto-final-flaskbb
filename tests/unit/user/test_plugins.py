# -*- coding: utf-8 -*-
"""
Testes novos da Tarefa 1.3, para o modulo flaskbb.user.plugins.

Este arquivo cobre as funcoes de hook que reunem os validadores usados
nas trocas de senha, email e detalhes do usuario. Sao testes de caminho
feliz, ou seja, verificam que cada funcao devolve exatamente os
validadores esperados, na ordem esperada, sem nenhuma condicao de erro
envolvida.
"""

import pytest

from flaskbb.user import plugins
from flaskbb.user.models import User
from flaskbb.user.services.validators import (
    CantShareEmailValidator,
    EmailsMustBeDifferent,
    OldEmailMustMatch,
    OldPasswordMustMatch,
    PasswordsMustBeDifferent,
    ValidateAvatarURL,
)

pytestmark = pytest.mark.usefixtures("default_settings")


class TestGatherPasswordValidators:
    def test_gather_password_validators_returns_expected_validators(self):
        # Caminho feliz, a funcao deve devolver os dois validadores de
        # senha, na mesma ordem em que estao escritos dentro da funcao
        # original, em flaskbb/user/plugins.py.
        result = plugins.flaskbb_gather_password_validators()

        assert len(result) == 2
        assert isinstance(result[0], OldPasswordMustMatch)
        assert isinstance(result[1], PasswordsMustBeDifferent)


class TestGatherEmailValidators:
    def test_gather_email_validators_returns_expected_validators(self):
        # Caminho feliz, aqui a funcao devolve tres validadores, o
        # terceiro precisa ser inicializado com a propria classe User,
        # entao conferimos isso tambem, nao so o tipo do validador.
        result = plugins.flaskbb_gather_email_validators()

        assert len(result) == 3
        assert isinstance(result[0], OldEmailMustMatch)
        assert isinstance(result[1], EmailsMustBeDifferent)
        assert isinstance(result[2], CantShareEmailValidator)
        assert result[2].users is User


class TestGatherDetailsUpdateValidators:
    def test_gather_details_update_validators_returns_expected_validator(self):
        # Caminho feliz, este hook so devolve um validador, o de avatar.
        result = plugins.flaskbb_gather_details_update_validators()

        assert len(result) == 1
        assert isinstance(result[0], ValidateAvatarURL)