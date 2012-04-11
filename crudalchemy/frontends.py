# handlers.py
# Copyright (C) 2012 the PyramidAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of PyramidAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from backends import SQLAlchemyBase

__all__ = ['SQLAlchemyProxy']


class BaseProxy(object):

    def __init__(self, model, backend):
        self.model = model
        self.backend = backend

    def create(self, context, request):
        raise NotImplemented

    def read(self, context, request):
        raise NotImplemented

    def update(self, context, request):
        raise NotImplemented

    def delete(self, context, request):
        raise NotImplemented

    def include_routes(self, config):
        # Route format: {cls}/{method}
        for method in ['create', 'read', 'update', 'delete']:
            name = '{}.{}'.format(self.model.__name__.lower(), method)
            pattern = '{}/{}'.format(self.model.__name__.lower(), method)
            config.add_route(name, pattern)

    def include_views(self, config, renderer='json'):
        for method in ['create', 'read', 'update', 'delete']:
            route_name = '{}.{}'.format(self.model.__name__.lower(), method)
            config.add_view(getattr(self, method),
                            route_name=route_name, renderer=renderer)

    def includeme(self, config):
        self.include_routes(config)
        self.include_views(config)


class SQLAlchemyProxy(BaseProxy):

    def __init__(self, model, backend=SQLAlchemyBase, session='session'):
        super(self, SQLAlchemyProxy).__init__(model, backend)
        self.backend = self.backend(self.model)
        self.session = session

    def get_params(self, request):

        # FIXME: check code! Registry was changed!
        params = {}

        for name in self.model.registry.attrs.iterkeys():

            if name in self.model.registry.excludes or\
              (self.model.registry.includes and
               name not in self.model.registry.includes) or\
              (name not in request.params and name not in request.matchdict):
                continue

            if name in self.model.registry.collections:
                params[name] = request.params.getall(name)

            elif name in request.matchdict:
                params[name] = request.matchdict.get(name)

            elif name in request.params:
                params[name] = request.params.get(name)

        return params

    def create(self, context, request):
        raise NotImplemented

    def read(self, context, request):
        raise NotImplemented

    def update(self, context, request):
        raise NotImplemented

    def delete(self, context, request):
        raise NotImplemented
