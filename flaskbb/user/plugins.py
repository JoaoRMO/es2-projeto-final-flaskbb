# -*- coding: utf-8 -*-
"""
flaskbb.user.plugins
~~~~~~~~~~~~~~~~~~~~

Plugin implementations for the FlaskBB user module.

:copyright: (c) 2018 the FlaskBB Team
:license: BSD, see LICENSE for details
"""

from itertools import chain

from flask_babelplus import gettext as _
from pluggy import HookimplMarker

from ..display.navigation import NavigationLink
from .models import User
from .services.validators import (
    CantShareEmailValidator,
    EmailsMustBeDifferent,
    OldEmailMustMatch,
    OldPasswordMustMatch,
    PasswordsMustBeDifferent,
    ValidateAvatarURL,
)

impl = HookimplMarker("flaskbb")


@impl(hookwrapper=True, tryfirst=True)
def flaskbb_tpl_profile_settings_menu():
    """
    Flattens the lists that come back from the hook
    into a single iterable that can be used to populate
    the menu
    """
    results = [
        (None, "Account Settings"),
        ("user.settings", "General Settings"),
        ("user.change_user_details", "Change User Details"),
        ("user.change_email", "Change E-Mail Address"),
        ("user.change_password", "Change Password"),
    ]
    outcome = yield
    outcome.force_result(chain(results, *outcome.get_result()))


@impl(hookwrapper=True, tryfirst=True)
def flaskbb_tpl_profile_links(user: User):
    """
    Adiciona os links padrao de navegacao do perfil, Overview, Topics e
    Posts, na frente dos links que outros plugins adicionarem.

    Esse hook usa o protocolo de hookwrapper do pluggy, o yield suspende
    a execucao ate que todas as outras implementacoes do hook rodem, e o
    valor delas chega em outcome.get_result(). Essa funcao concatena a
    propria lista de links, na frente, com o resultado de todo mundo, e
    substitui o resultado final com outcome.force_result(...).
    """
    results = [
        NavigationLink(
            endpoint="user.profile",
            name=_("Overview"),
            icon="fa fa-home",
            urlforkwargs={"username": user.username},
        ),
        NavigationLink(
            endpoint="user.view_all_topics",
            name=_("Topics"),
            icon="fa fa-comments",
            urlforkwargs={"username": user.username},
        ),
        NavigationLink(
            endpoint="user.view_all_posts",
            name=_("Posts"),
            icon="fa fa-comment",
            urlforkwargs={"username": user.username},
        ),
    ]
    outcome = yield
    outcome.force_result(chain(results, *outcome.get_result()))


@impl
def flaskbb_gather_password_validators():
    """
    Ponto de extensao do pluggy para registrar validadores de troca de
    senha. Cada plugin instalado pode implementar esse hook e devolver
    sua propria lista de validadores, o pluggy chama todas as
    implementacoes registradas e o resultado de cada uma vira um item da
    lista de listas que password_update_handler (em
    services/factories.py) achata com chain.from_iterable antes de
    montar o handler de senha.
    """
    return [OldPasswordMustMatch(), PasswordsMustBeDifferent()]


@impl
def flaskbb_gather_email_validators():
    """
    Ponto de extensao do pluggy para registrar validadores de troca de
    email, no mesmo esquema de flaskbb_gather_password_validators, mas
    para o fluxo de email, consumido por email_update_handler em
    services/factories.py.
    """
    return [OldEmailMustMatch(), EmailsMustBeDifferent(), CantShareEmailValidator(User)]


@impl
def flaskbb_gather_details_update_validators():
    """
    Ponto de extensao do pluggy para registrar validadores de troca dos
    detalhes do usuario, avatar, bio e afins, consumido por
    details_update_factory em services/factories.py.
    """
    return [ValidateAvatarURL()]