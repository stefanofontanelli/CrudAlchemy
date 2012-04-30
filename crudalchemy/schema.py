# schema.py
# Copyright (C) 2012 the CrudAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of CrudAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from sqlalchemy.orm import object_mapper
from colanderalchemy import SQLAlchemyMapping


__all__ = ['CreateSchema', 'ReadSchema', 'UpdateSchema', 'DeleteSchema']


class Base(SQLAlchemyMapping):

    def serialize(self, obj):
        return super(Base, self).serialize(self.dictify(obj))

    def deserialize(self, struct):
        return self._reg.cls(**super(Base, self).deserialize(struct))

    def dictify(self, obj):

        dict_ = {}
        # FIXME: check code! Registry was changed!
        for name in self._reg.attrs.iterkeys():

            if name in self._reg.excludes or \
              (self._reg.includes and name not in self._reg.includes):
                continue

            if name in self._reg.fields:
                dict_[name] = getattr(obj, name)

            elif name in self.schema.registry.references:
                value = getattr(obj, name)
                if not value is None:
                    value = self.dictify_relationship(value)
                dict_[name] = value

            elif name in self.schema.registry.collections:
                dict_[name] = [self.dictify_relationship(value)
                               for value in getattr(obj, name)]

        return dict_

    def dictify_relationship(self, obj):
        dict_ = {}
        for col in object_mapper(obj).primary_key:
            dict_[col.name] = getattr(obj, col.name)
        return dict_


class CreateSchema(Base):

    def __init__(self, cls):
        # Build internal registry.
        super(CreateSchema, self).__init__(cls)
        # Keep PKs optional: can be useful when PK is autoincrement.
        nullables = {name:True for name in self._reg.pkeys}
        super(CreateSchema, self).__init__(cls, nullables=nullables)


class UpdateSchema(Base):
    """ Default behaviour is enough. """
    pass


class DeleteSchema(Base):

    def __init__(self, cls):
        # First step: build internal registry.
        super(DeleteSchema, self).__init__(cls)
        # During delete are needed PKs only.
        includes = self._reg.pkeys
        super(DeleteSchema, self).__init__(cls, includes=includes)
