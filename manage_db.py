from sqlalchemy.sql import insert, update
from sqlalchemy import create_engine, text, Table, Column, String, MetaData
from flask import Flask, request, redirect, render_template
import os
#import config

def connect_db(app):
	engine = create_engine(os.environ['CLEARDB_DATABASE_URL'], encoding = 'utf-8', convert_unicode=False, pool_size=20, pool_recycle=500, max_overflow=20)
#	engine = create_engine(config.DB_URL, encoding = 'utf-8', convert_unicode=False, pool_size=20, pool_recycle=500, max_overflow=20)

	meta = MetaData()
	auth_info_table = Table(
		'auth', meta,
		Column('user_id',String(20), primary_key=True),
		Column('token',String(64)),
	)
	meta.create_all(engine)
	return auth_info_table, engine


def get_update_query(table, user_id, token):
	update_query = update(table)
	update_query = update_query.values({"token": token})
	update_query = update_query.where(table.c.user_id == user_id)
	return update_query


def get_insert_query(table, user_id, token):
	insert_query = insert(table)
	insert_query = insert_query.values({"user_id":user_id, "token":token})
	return (insert_query)
