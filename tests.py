# tests.py
# Copyright (C) 2012 the CrudAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of CrudAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import crudalchemy
import logging
import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
from sqlalchemy.orm.exc import NoResultFound
import sqlalchemy.schema
import unittest


log = logging.getLogger(__name__)
Base = sqlalchemy.ext.declarative.declarative_base()


class Account(Base, crudalchemy.CRUDBase):
    __tablename__ = 'accounts'
    email = sqlalchemy.Column(sqlalchemy.Unicode(256), primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.Unicode(128), nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.Unicode(128), nullable=True)
    gender = sqlalchemy.Column(sqlalchemy.Enum(u'M', u'F'), nullable=True)
    contact = sqlalchemy.orm.relationship('Contact',
                                          uselist=False,
                                          back_populates='account')


class Contact(Base, crudalchemy.CRUDBase):
    __tablename__ = 'contacts'
    type_ = sqlalchemy.Column(sqlalchemy.Unicode(256), primary_key=True)
    value = sqlalchemy.Column(sqlalchemy.Unicode(256), nullable=False)
    account_id = sqlalchemy.Column(sqlalchemy.Unicode(256),
                                   sqlalchemy.ForeignKey('accounts.email'),
                                   primary_key=True)
    account = sqlalchemy.orm.relationship('Account', back_populates='contact')


class TestsBase(unittest.TestCase):

    def setUp(self):
        self.engine = sqlalchemy.create_engine('sqlite://', echo=False)
        Base.metadata.bind = self.engine
        Base.metadata.create_all(self.engine)
        self.Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.session = self.Session()

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    def test_crud(self):
        # Test Create.
        accounts = self.create_accounts()
        self.session.flush()
        # Test Read.
        self.assertEqual(sorted(accounts),
                         sorted(Account.search(self.session)))

        self.assertEqual(Account.search(self.session,
                                        raw_query=True).count(),
                         2)

        self.assertEqual(Account.search(self.session,
                                        start=0,
                                        limit=1)[0].email,
                         accounts[0].email)
        self.assertEqual(Account.search(self.session,
                                        start=1,
                                        limit=2)[0].email,
                         accounts[1].email)

        criterions = (Account.email.like('%domain.%'),)
        self.assertEqual(Account.search(self.session,
                                        *criterions)[0].email,
                         accounts[0].email)

        order_by = (Account.gender.asc(),)
        self.assertEqual(Account.search(self.session,
                                        order_by=order_by)[0].email,
                         accounts[1].email)
        self.assertEqual(Account.search(self.session,
                                        order_by=order_by)[1].email,
                         accounts[0].email)

        order_by = (Account.gender.desc(),)
        self.assertEqual(Account.search(self.session,
                                        order_by=order_by)[0].email,
                         accounts[0].email)
        self.assertEqual(Account.search(self.session,
                                        order_by=order_by)[1].email,
                         accounts[1].email)

        criterions = (Account.email.like('%domain%'),
                      Account.gender == 'F')
        self.assertEqual(Account.search(self.session,
                                        *criterions)[0].email,
                         accounts[1].email)

        criterions = (Account.gender == 'M',
                      Account.gender == 'F')
        results = Account.search(self.session,
                                 intersect=False,
                                 *criterions)
        self.assertIn(accounts[0], results)
        self.assertIn(accounts[1], results)

        results = Account.search(self.session,
                                 intersect=False,
                                 start=0,
                                 *criterions)
        self.assertIn(accounts[0], results)
        self.assertIn(accounts[1], results)

        results = Account.search(self.session,
                                 intersect=False,
                                 limit=1,
                                 *criterions)
        self.assertIn(accounts[0], results)
        self.assertNotIn(accounts[1], results)

        self.assertRaises(ValueError,
                          Account.search,
                          self.session,
                          start=0,
                          limit=1,
                          raw_query=True)

        # Test read
        params = {'email': 'mailbox@domain.tld'}
        obj = Account.read(self.session, **params)
        self.assertEqual(accounts[0], obj)

        self.assertRaises(ValueError,
                          Account.read,
                          self.session)

        # Test Update
        self.update_accounts()

        # Test Bulk Update
        self.bulk_update_accounts()

        # Test Delete
        self.delete_accounts()

        # Test Delete
        self.bulk_delete_accounts()

    def create_accounts(self):
        accounts = [Account.create(self.session, **params)
                    for params in [{'email': 'mailbox@domain.tld',
                                    'name': 'My Name',
                                    'surname': 'My Surname',
                                    'gender': 'M'},
                                   {'email': 'mailbox2@domain2.tld',
                                    'name': 'My Name 2',
                                    'surname': 'My Surname 2',
                                    'gender': 'F'}]
                    ]
        return accounts

    def update_accounts(self):
        params = {'email': 'mymailbox@domain.tld',
                  'name': 'My Name',
                  'surname': 'My Surname',
                  'gender': 'M'}
        self.assertRaises(NoResultFound,
                          Account.update,
                          self.session,
                          **params)
        params = {'email': 'mailbox@domain.tld',
                  'name': 'My New Cool Name',
                  'surname': 'My New Cool Surname',
                  'gender': 'M'}
        obj = Account.update(self.session, **params)
        self.session.flush()
        criterions = (Account.email == 'mailbox@domain.tld',)
        account = Account.search(self.session, *criterions)[0]
        self.assertEqual(obj.name, account.name)
        self.assertEqual(obj.surname, account.surname)

    def bulk_update_accounts(self):
        params = {'email': 'mailbox@domain.tld',
                  'name': 'My New Cool Name 2',
                  'surname': 'My New Cool Surname 2',
                  'gender': 'F'}
        i = Account.update(self.session, bulk=True, **params)
        self.session.flush()
        self.assertEqual(i, 1)

    def delete_accounts(self):
        self.assertRaises(NoResultFound,
                          Account.delete,
                          self.session,
                          email='nomail@nodomain.tld')
        Account.delete(self.session, email='mailbox@domain.tld')
        self.session.flush()
        self.assertEqual(Account.search(self.session,
                                        raw_query=True).count(),
                         1)

    def bulk_delete_accounts(self):
        Account.delete(self.session, bulk=True, email='mailbox2@domain2.tld')
        self.session.flush()
        self.assertEqual(Account.search(self.session,
                                        raw_query=True).count(),
                         0)
