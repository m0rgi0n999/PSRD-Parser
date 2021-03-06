import json
import sys
import os
from psrd.sql import get_db_connection
from psrd.sql import fetch_top, append_child_section, fetch_section, update_section
from psrd.sql.section_index import fetch_indexable_sections, count_sections_with_name, fetch_index, insert_index, strip_unindexed_urls, update_link_create_index
from psrd.sql.index.section_sort import create_sorts

def save_index(curs, section_id, search_name, type_name):
	fetch_index(curs, section_id, search_name)
	if not curs.fetchone():
		insert_index(curs, section_id, search_name, type_name)

def index_section(curs, section):
	if section['create_index'] != 1:
		if section['name'] == section['parent_name']:
			if section['type'] == 'section':
				# if a section has the same name as it's parent and it is not
				# a more interesting type then 'section', don't index it
				return
	if section['type'] != 'section':
		save_index(curs, section['section_id'], section['name'], section['type'])
	elif section['subtype'] != None:
		save_index(curs, section['section_id'], section['name'], section['type'])
	else:
		count_sections_with_name(curs, section['name'])
		rec = curs.fetchone()
		if rec['cnt'] <= 5:
			save_index(curs, section['section_id'], section['name'], section['type'])
		elif section['create_index'] == 1:
			save_index(curs, section['section_id'], section['name'], section['type'])

def build_default_index(db, conn):
	curs = conn.cursor()
	try:
		update_link_create_index(curs)
		fetch_indexable_sections(curs)
		section = curs.fetchone()
		while section:
			index_section(conn.cursor(), section)
			section = curs.fetchone()
		conn.commit()
	finally:
		curs.close()

def strip_urls(conn):
	curs = conn.cursor()
	try:
		strip_unindexed_urls(curs)
		conn.commit()
	finally:
		curs.close()

def load_section_index(db, args, parent):
	conn = get_db_connection(db)
	build_default_index(db, conn)
	strip_urls(conn)
