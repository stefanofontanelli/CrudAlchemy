# tests.py
# Copyright (C) 2012 the CrudAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of CrudAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php


import colander
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


class Account(Base):
    __tablename__ = 'accounts'
    email = sqlalchemy.Column(sqlalchemy.Unicode(256), primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.Unicode(128), nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.Unicode(128), nullable=False)
    gender = sqlalchemy.Column(sqlalchemy.Enum(u'M', u'F'), nullable=False)
    contact = sqlalchemy.orm.relationship('Contact',
                                          uselist=False,
                                          back_populates='account')


class Contact(Base):
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
        self.account = crudalchemy.Base(Account)
        self.contact = crudalchemy.Base(Contact)

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    def test_crud(self):
        # Test Create.
        accounts = self.create_accounts()
        self.session.flush()
        # Test Read.
        self.assertEqual(sorted(accounts),
                         sorted(self.account.read(self.session)))

        self.assertEqual(self.account.read(self.session,
                                           raw_query=True).count(),
                         2)

        self.assertEqual(self.account.read(self.session,
                                           start=0,
                                           limit=1)[0].email,
                         accounts[0].email)
        self.assertEqual(self.account.read(self.session,
                                           start=1,
                                           limit=2)[0].email,
                         accounts[1].email)

        criterions = (Account.email.like('%domain.%'),)
        self.assertEqual(self.account.read(self.session,
                                           criterions=criterions)[0].email,
                         accounts[0].email)

        order_by = (Account.gender.asc(),)
        self.assertEqual(self.account.read(self.session,
                                           order_by=order_by)[0].email,
                         accounts[1].email)
        self.assertEqual(self.account.read(self.session,
                                           order_by=order_by)[1].email,
                         accounts[0].email)

        order_by = (Account.gender.desc(),)
        self.assertEqual(self.account.read(self.session,
                                           order_by=order_by)[0].email,
                         accounts[0].email)
        self.assertEqual(self.account.read(self.session,
                                           order_by=order_by)[1].email,
                         accounts[1].email)

        criterions = (Account.email.like('%domain%'),
                      Account.gender == 'F')
        self.assertEqual(self.account.read(self.session,
                                           criterions=criterions)[0].email,
                         accounts[1].email)

        criterions = (Account.gender == 'M',
                      Account.gender == 'F')
        results = self.account.read(self.session,
                                    criterions=criterions,
                                    intersect=False)
        self.assertIn(accounts[0], results)
        self.assertIn(accounts[1], results)

        # Test Update
        self.update_accounts()

        # Test Delete
        self.delete_accounts()

    def create_accounts(self):
        accounts = [self.account.create(self.session, **params)
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
        params = {'name': 'My Name',
                  'surname': 'My Surname',
                  'gender': 'M'}
        self.assertRaises(colander.Invalid,
                          self.account.update,
                          self.session,
                          **params)
        params = {'email': 'mymailbox@domain.tld',
                  'name': 'My Name',
                  'surname': 'My Surname',
                  'gender': 'M'}
        self.assertRaises(NoResultFound,
                          self.account.update,
                          self.session,
                          **params)
        params = {'email': 'mailbox@domain.tld',
                  'name': 'My New Cool Name',
                  'surname': 'My New Cool Surname',
                  'gender': 'M'}
        obj = self.account.update(self.session, **params)
        self.session.flush()
        criterions = (Account.email == 'mailbox@domain.tld',)
        account = self.account.read(self.session, criterions=criterions)[0]
        self.assertEqual(obj.name, account.name)
        self.assertEqual(obj.surname, account.surname)

    def delete_accounts(self):
        self.assertRaises(NoResultFound,
                          self.account.delete,
                          self.session,
                          email='nomail@nodomain.tld')
        self.account.delete(self.session, email='mailbox@domain.tld')
        self.account.delete(self.session, email='mailbox2@domain2.tld')
        self.session.flush()
        self.assertEqual(self.account.read(self.session,
                                           raw_query=True).count(),
                         0)
