# views.py
# Copyright (C) 2012 the ColanderAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of PyramidCRUD and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

__all__ = ['SQLAlchemyBase']


class SQLAlchemyBase(object):

    def __init__(self, mapped_cls):
        self.mapped_cls = mapped_cls

    def create(self, session, **kwargs):
        obj = self.mapped_cls(**kwargs)
        session.add(obj)
        return obj

    def read(self, session, criterions=None, logical_conjunction=None,
             order_by=None, start=None, limit=None):

        query = session.query(self.mapped_cls)

        if not criterions is None and not logical_conjunction is None:
            query = query.filter(logical_conjunction(*criterions))

        elif not criterions is None:
            query = query.filter(*criterions)

        if not order_by is None:
            query = query.order_by(*order_by)

        if not start is None and not limit is None:
            end = start + limit
            return query[start:end]

        elif not start is None and limit is None:
            return query[start:]

        elif start is None and not limit is None:
            return query[:limit]

        # start is None and limit is None:
        return query.all()

    def update(self, session, **kwargs):
        obj = self.mapped_cls(**kwargs)
        obj = session.merge(obj)
        return obj

    def delete(self, session, **kwargs):
        obj = self.mapped_cls(**kwargs)
        obj = session.merge(obj)
        session.delete(obj)
        return obj
