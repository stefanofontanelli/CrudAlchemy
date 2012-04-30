# __init__.py
# Copyright (C) 2012 the CrudAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of CrudAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from schema import CreateSchema
from schema import UpdateSchema
from schema import DeleteSchema
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.expression import or_

__all__ = ['Base']


class Base(object):

    def __init__(self,
                 cls,
                 create_schema=CreateSchema,
                 update_schema=UpdateSchema,
                 delete_schema=DeleteSchema):
        self.model = cls
        self.create_schema = create_schema(cls)
        self.update_schema = update_schema(cls)
        self.delete_schema = delete_schema(cls)

    def create(self, session, **kwargs):
        obj = self.create_schema.deserialize(kwargs)
        session.add(obj)
        return obj

    def read(self, session, criterions=None, intersect=True,
             order_by=None, start=None, limit=None, raw_query=False):

        query = session.query(self.model)

        if criterions and intersect:
            # Use sqlalchmey AND
            query = query.filter(and_(*criterions))

        elif criterions:
            # Use sqlalchmey OR
            query = query.filter(or_(*criterions))

        if order_by:
            query = query.order_by(*order_by)

        if not raw_query and not start is None and not limit is None:
            end = start + limit
            return query[start:end]

        elif not raw_query and not start is None and limit is None:
            return query[start:]

        elif not raw_query and start is None and not limit is None:
            return query[:limit]

        elif not raw_query and start is None and limit is None:
            return query.all()

        elif raw_query and start is None and limit is None:
            return query

        msg = "'raw_query' and 'start'/'limit' are mutually exclusive."
        raise ValueError(msg)

    def update(self, session, **kwargs):
        # FIXME: add support to update of PKs.
        obj = self.update_schema.deserialize(kwargs)
        obj = session.merge(obj)
        if obj in session.new:
            session.expunge(obj)
            pkeys = [getattr(obj, attr)
                     for attr in self.update_schema.registry.pkeys]
            msg = "%s %s not found." % (self.model.__name__, pkeys)
            raise NoResultFound(msg)
        return obj

    def delete(self, session, **kwargs):
        # Add checks. An example: no entity -> raise NoResultFound
        obj = self.delete_schema.deserialize(kwargs)
        obj = session.merge(obj)
        if obj in session.new:
            session.expunge(obj)
            pkeys = [getattr(obj, attr)
                     for attr in self.delete_schema.registry.pkeys]
            msg = "%s %s not found." % (self.model.__name__, pkeys)
            raise NoResultFound(msg)
        session.delete(obj)
        return obj
