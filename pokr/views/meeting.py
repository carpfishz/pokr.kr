#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from datetime import date
import os.path
import re

from flask import abort, current_app, render_template, redirect, request, send_file, url_for
from flask.ext.babel import gettext, format_date
from sqlalchemy.orm import undefer, undefer_group
from sqlalchemy.orm.exc import NoResultFound

from pokr.cache import cache
from pokr.database import db_session
from pokr.models.meeting import Meeting
from pokr.widgets.year import year
from utils.jinja import breadcrumb


date_re = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def latest_meeting_date(year):
    date_ =  db_session.query(Meeting.date)\
                       .filter(Meeting.year == year)\
                       .order_by(Meeting.date.desc())\
                       .first()
    return date_[0] if date_ else None


def register(app):
    app.views['meeting'] = 'meeting_main'
    gettext('meeting') # for babel extraction

    @app.route('/meeting/', methods=['GET'])
    @breadcrumb(app)
    def meeting_main():
        year = request.args.get('year')
        date_ = request.args.get('date')

        # find the right calendar
        if not year:
            if date_:
                year = format_date(date(*map(int, date_.split('-'))), 'yyyy')
            else:
                year = date.today().year

        if not date_:
            # find the latest meeting date for the selected year
            d = latest_meeting_date(year)
            if d:
                return redirect(url_for('meeting_main',
                                        date=format_date(d, 'yyyy-MM-dd')))

        # meetings of the day (optional)
        meetings_of_the_day = None
        if date_:
            if not date_re.match(date_):
                abort(404)
            date_ = date(*map(int, date_.split('-')))
            meetings_of_the_day = Meeting.query.filter_by(date=date_)

        # meetings of the year
        meetings_of_the_year =\
                db_session.query(Meeting.date)\
                          .filter(Meeting.year == year)\
                          .group_by(Meeting.date)
        meetings_of_the_year = (
            {
                'date': meeting_date,
                'url': url_for('meeting_main',
                               date=format_date(meeting_date, 'yyyy-MM-dd'))
            }
            for (meeting_date,) in meetings_of_the_year
        )

        return render_template('meetings.html',
                               year=int(year),
                               date=date_,
                               meetings_of_the_year=meetings_of_the_year,
                               meetings_of_the_day=meetings_of_the_day,
                              )

    @app.route('/meeting/<id>/', methods=['GET'])
    @breadcrumb(app, 'meeting')
    def meeting(id):
        try:
            meeting = Meeting.query.filter_by(id=id)\
                             .options(undefer('issues')).one()
        except NoResultFound, e:
            abort(404)

        return render_template('meeting.html', meeting=meeting)

    @app.route('/meeting/<id>/dialog', methods=['GET'])
    @breadcrumb(app, 'meeting')
    def meeting_dialogue(id):
        glossary_js = generate_glossary_js()
        try:
            meeting = Meeting.query.filter_by(id=id)\
                             .options(undefer_group('extra')).one()
        except NoResultFound, e:
            abort(404)

        return render_template('meeting-dialogue.html',\
                meeting=meeting, glossary_js=glossary_js)

    @app.route('/meeting/<id>/pdf', methods=['GET'])
    def meeting_pdf(id):
        try:
            meeting = Meeting.query.filter_by(id=id).one()
        except NoResultFound, e:
            abort(404)

        if meeting.document_pdf_path:
            response = send_file(meeting.document_pdf_path)
            response.headers['Content-Disposition'] = 'filename=%s.pdf' % id
            return response
        else:
            abort(404)


@cache.memoize(timeout=60*60*24)
def generate_glossary_js():
    datadir = os.path.join(current_app.root_path, 'data')
    terms_regex = open('%s/glossary-terms.regex' % datadir).read().decode('utf-8').strip()
    dictionary = open('%s/glossary-map.json' % datadir).read().decode('utf-8').strip()
    return render_template('js/glossary.js', terms_regex=terms_regex,
            dictionary=dictionary)
