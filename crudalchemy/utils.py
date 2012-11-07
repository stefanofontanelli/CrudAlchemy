# Copyright (C) 2012 the CrudAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of CrudAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
import logging

__all__ = ['setup_sqlalchemy']


log = logging.getLogger(__file__)


def setup_sqlalchemy(config, settings, base,
                     req_prop_fun='crudalchemy.create_sqla_session',
                     req_prop_name='db_session'):
    """ Utility function usefull to config SQLA in Pyramid apps.
    """
    config.set_request_property(req_prop_fun,
                                name=request_property,
                                reify=True)
    init_model(config, settings, base)


def create_sqla_session(request):
    """Create and return the request's SQLAlchemy session.
    """

    session = request.registry.scoped_session()

    def destroy_sqla_session(_):
        """ Callback handler for the "finished" request event """
        log.debug("Destroy SQLAlchemy session.")
        session.close()

    request.add_finished_callback(destroy_sqla_session)
    log.debug("Create SQLAlchemy session.")
    return session


def init_model(config, settings, base):
    """Set up SQLAlchemy models.
    """
    engine = engine_from_config(settings, prefix='sqlalchemy.')
    config.registry.db_engine = engine
    config.registry.scoped_session = scoped_session(sessionmaker(bind=engine))
    base.metadata.bind = engine
    base.metadata.create_all(engine)
