#!/usr/bin/env python
# -*- coding: utf-8 -*-

import colanderalchemy
import sqlalchemy.sql.expression


class Controller(object):

    def __init__(self, entity):
        super(Controller, self).__init__()
        self.entity = entity
        self.schema = colanderalchemy.get_schema(entity)
        self.registry = colanderalchemy.get_registry(self.schema)

    def create(self, session, **params):
        params = self.validate_params(session, **params)
        obj = self.entity(**params)
        session.add(obj)
        return obj

    def read(self, session, criterions=[],
             conjunction='and', start=None, limit=None, raw_query=False):

        query = session.query(self.entity)

        if conjunction == 'and':
            conjunction = getattr(sqlalchemy.sql.expression, 'and_')
        elif conjunction == 'or':
            conjunction = getattr(sqlalchemy.sql.expression, 'or_')
        else:
            raise ValueError('Unknown conjunction value: %s', conjunction)

        if criterions:
            query = query.filter(conjunction(**criterions))

        if raw_query:
            return query

        if not start is None and not limit is None:
            end = start + limit
            return query[start:end]

        elif not start is None and limit is None:
            return query[start:]

        elif start is None and not limit is None:
            return query[:limit]

        return query.all()

    def update(self, session, **params):
        params = self.validate_params(session, **params)
        obj = self.entity(**params)
        return session.merge(obj)

    def delete(self, session, **params):
        params = self.validate_params(session, **params)
        obj = self.entity(**params)
        session.delete(session.merge(obj))

    def validate_params(self, session, **params):
        # Add checks for relationships params!
        # They must exist in the database!
        for name, cls in self.registry.relationships.iteritems():
            validator = colanderalchemy.RelationshipValidator(session, cls)
            self.schema[name].validator = validator
        # Read params from the request.
        return self.schema.deserialize(params)

    def dictify(self, obj):

        dict_ = {}
        mapper = sqlalchemy.orm.object_mapper(obj)
        for prop in mapper.iterate_properties:

            if isinstance(prop, sqlalchemy.orm.properties.ColumnProperty):
                dict_[prop.key] = getattr(obj, prop.key)

            elif isinstance(prop,
                            sqlalchemy.orm.properties.RelationshipProperty):

                if callable(prop.argument):
                    cls = prop.argument()

                else:
                    cls = prop.argument.class_

                pks = sqlalchemy.orm.class_mapper(cls).primary_key
                if len(pks) > 1:
                    msg = 'Composite primary keys are not supported.'
                    raise NotImplemented(msg)

                rel = getattr(obj, prop.key)

                if not prop.uselist:
                    dict_[prop.key] = getattr(rel, pks[0])

                else:
                    dict_[prop.key] = [getattr(o, pks[0]) for o in rel]

            else:
                NotImplemented('Unsupported property type: %s' % prop)

        return dict_
