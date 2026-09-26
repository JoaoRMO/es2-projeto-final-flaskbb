# -*- coding: utf-8 -*-
"""
Testes novos da Tarefa 1.3, para o modulo flaskbb.user.services.factories.

Este modulo nao tinha nenhum teste proprio antes deste projeto, por isso
a cobertura dele estava em 0% na baseline, registrada em
parte1/BASELINE.md. Os testes abaixo verificam que cada funcao de
fabrica devolve o objeto certo, e que a integracao com os hooks do
pluggy, definidos em flaskbb.user.plugins, realmente acontece.
"""

import pytest
from flask_login import login_user

from flaskbb.extensions import db, pluggy
from flaskbb.user.forms import ChangeEmailForm
from flaskbb.user.services import factories
from flaskbb.user.services.update import (
    DefaultDetailsUpdateHandler,
    DefaultEmailUpdateHandler,
    DefaultPasswordUpdateHandler,
    DefaultSettingsUpdateHandler,
)
from flaskbb.user.services.validators import (
    CantShareEmailValidator,
    EmailsMustBeDifferent,
    OldEmailMustMatch,
    OldPasswordMustMatch,
    PasswordsMustBeDifferent,
)

pytestmark = pytest.mark.usefixtures("default_settings")


class TestSettingsUpdateHandler:
    def test_settings_update_handler_returns_configured_handler(self):
        # Caminho feliz, esta fabrica e a mais simples do arquivo, ela
        # nao depende de nenhum hook, so devolve o handler ja configurado
        # com o banco de dados e o gerenciador de plugins do projeto.
        handler = factories.settings_update_handler()

        assert isinstance(handler, DefaultSettingsUpdateHandler)
        assert handler.db is db
        assert handler.plugin_manager is pluggy


class TestDetailsUpdateFactory:
    def test_details_update_factory_gathers_real_validator_from_hook(self):
        # Borda, aqui a fabrica realmente aciona o hook do pluggy, por
        # isso o teste verifica a integracao entre a fabrica e o hook
        # definido em flaskbb/user/plugins.py, e nao so o tipo devolvido.
        handler = factories.details_update_factory()

        assert isinstance(handler, DefaultDetailsUpdateHandler)
        assert len(handler.validators) == 1


class TestPasswordUpdateHandlerFactory:
    def test_password_update_handler_gathers_real_validators_from_hook(self):
        # Borda, mesma ideia do teste anterior, agora para os
        # validadores de senha, que devem vir na ordem definida em
        # flaskbb/user/plugins.py.
        handler = factories.password_update_handler()

        assert isinstance(handler, DefaultPasswordUpdateHandler)
        assert len(handler.validators) == 2
        assert isinstance(handler.validators[0], OldPasswordMustMatch)
        assert isinstance(handler.validators[1], PasswordsMustBeDifferent)


class TestEmailUpdateHandlerFactory:
    def test_email_update_handler_gathers_real_validators_from_hook(self):
        # Borda, mesma ideia, agora para os tres validadores de troca de
        # email.
        handler = factories.email_update_handler()

        assert isinstance(handler, DefaultEmailUpdateHandler)
        assert len(handler.validators) == 3
        assert isinstance(handler.validators[0], OldEmailMustMatch)
        assert isinstance(handler.validators[1], EmailsMustBeDifferent)
        assert isinstance(handler.validators[2], CantShareEmailValidator)


class TestChangeEmailFormFactory:
    def test_change_email_form_factory_binds_current_user(
        self, user, post_request_context
    ):
        # Caminho feliz, esta fabrica precisa de um usuario logado de
        # verdade, por isso usamos login_user dentro de um contexto de
        # requisicao, do mesmo jeito que os testes de views do proprio
        # projeto ja fazem. O construtor de ChangeEmailForm guarda o
        # usuario recebido em self.user, entao conferimos isso tambem.
        login_user(user)

        form = factories.change_email_form_factory()

        assert isinstance(form, ChangeEmailForm)
        # assert form.user is user
        assert form.user.id == user.id