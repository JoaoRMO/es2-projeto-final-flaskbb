# -*- coding: utf-8 -*-
"""
Teste com mock da Tarefa 1.5, para o modulo
flaskbb.user.services.factories.

Este teste isola o hook do pluggy dentro da fabrica
password_update_handler, substituindo o gerenciador de plugins inteiro
por um dublê, para nao depender dos validadores reais registrados em
flaskbb/user/plugins.py. O dublê so isola essa dependencia externa, o
banco de dados (db) continua sendo o real, sem substituicao, e o foco
do teste continua sendo o comportamento da propria fabrica, conferindo
que ela chama o hook uma unica vez, com o argumento correto, e monta o
handler com exatamente os validadores que o dublê devolveu.
"""

from flaskbb.extensions import db
from flaskbb.user.services import factories
from flaskbb.user.services.update import DefaultPasswordUpdateHandler


class TestPasswordUpdateHandlerFactoryComMock:
    def test_password_update_handler_aciona_o_hook_uma_vez(
        self, mocker, application
    ):
        validador_falso_1 = mocker.Mock()
        validador_falso_2 = mocker.Mock()
        pluggy_falso = mocker.MagicMock()
        pluggy_falso.hook.flaskbb_gather_password_validators.return_value = [
            [validador_falso_1, validador_falso_2]
        ]
        mocker.patch("flaskbb.user.services.factories.pluggy", pluggy_falso)

        handler = factories.password_update_handler()

        # Verifica a interacao com o dublê, o hook precisa ser chamado
        # exatamente uma vez, e com o app correto.
        pluggy_falso.hook.flaskbb_gather_password_validators.assert_called_once_with(
            app=application
        )

        # Verifica que o handler foi montado com os validadores que o
        # dublê devolveu, e que o banco de dados continua sendo o real,
        # sem nenhuma substituicao.
        assert isinstance(handler, DefaultPasswordUpdateHandler)
        assert handler.db is db
        assert handler.plugin_manager is pluggy_falso
        assert handler.validators == [validador_falso_1, validador_falso_2]