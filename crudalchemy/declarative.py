# Copyright (C) 2012 the CrudAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of CrudAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from sqlalchemy import inspect
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.expression import or_
import logging


__all__ = ['CRUDBase']


log = logging.getLogger(__file__)


class CRUDBase(object):

    @classmethod
    def create(cls, session, **kwargs):
        obj = cls(**kwargs)
        session.add(obj)
        return obj

    @classmethod
    def read(cls, session, **kwargs):

        try:
            id_ = tuple([kwargs.pop(prop.key)
                         for prop in inspect(cls).column_attrs
                         if prop.columns[0].primary_key])

        except KeyError as e:
            msg = 'You must specify all primary keys: %s' % e
            raise ValueError(msg)

        obj = session.query(cls).get(id_)
        if obj is None:
            msg = '%s %s not found.' % (cls.__name__, kwargs)
            raise NoResultFound(msg)

        return obj

    @classmethod
    def search(cls, session, *criterions, **kwargs):

        intersect = kwargs.pop('intersect', True)
        order_by = kwargs.pop('order_by', None)
        start = kwargs.pop('start', None)
        limit = kwargs.pop('limit', None)
        raw_query = kwargs.pop('raw_query', False)

        query = session.query(cls)

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

    @classmethod
    def update(cls, session, bulk=False, sync_session='evaluate', **kwargs):

        # NOTE:  update of PKs is not supported.
        # It can be done after using returned obj.
        if not bulk:
            obj = cls.read(session, **kwargs)
            for attr, value in kwargs.items():
                log.debug('Attr: %s - Value: %s' % (attr, value))
                setattr(obj, attr, value)
            return obj

        else:
            criterions = [getattr(cls, prop.key) == kwargs.pop(prop.key)
                          for prop in inspect(cls).column_attrs
                          if prop.key in kwargs and \
                             prop.columns[0].primary_key]
            query = cls.search(session, raw_query=True, *criterions)
            return query.update(kwargs, sync_session)

    @classmethod
    def delete(cls, session, bulk=False, sync_session='evaluate', **kwargs):
        if not bulk:
            obj = cls.read(session, **kwargs)
            session.delete(obj)
        else:
            criterions = [getattr(cls, attr) == value
                          for attr, value in kwargs.items()]
            query = cls.search(session, raw_query=True, *criterions)
            return query.delete(sync_session)
