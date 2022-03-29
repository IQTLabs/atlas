import asyncio
import os
from datetime import datetime

import babel
from application.dashapp.load_elements import load_elements
from application.forms import ViewForm, DeleteViewForm
from application.gql import get_hasura_connection, get_hasura_connection_with_params
from application.queries import getAuthenticatedUser, getMyViews, getFeaturedViews, insertView, softDeleteMyView, \
    insertLayout, insertDataOne, insertNode, updateDataById
from flask import g, Blueprint, render_template, request, redirect, abort, current_app
from werkzeug.utils import secure_filename
import secrets
import json

server_bp = Blueprint(
    'main', __name__,
    static_folder='static'
)


@server_bp.before_request
def generate_nonce(length=8):
    g.nonce = secrets.token_urlsafe()


@server_bp.after_request
def add_security_headers(resp):
    if current_app.config.get('FLASK_ENV') == 'public':
        resp.headers['Content-Security-Policy'] = f"default-src 'none'; script-src 'self' 'nonce-{g.nonce}' http://www.googletagmanager.com https://code.jquery.com; connect-src 'self' https://www.google-analytics.com; img-src 'self' https://assets.iqt.org; base-uri 'self'; form-action 'self'; font-src 'self'; style-src 'self' 'nonce-{g.nonce}'"
        resp.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains; preload'
    return resp

@server_bp.route('/terms_of_use', methods=['GET'])
def terms_of_use():
    return render_template('terms_of_use.html')

@server_bp.route('/privacy_policy', methods=['GET'])
def privacy_policy():
    return render_template('privacy_policy.html')


@server_bp.route('/', methods=['GET', 'POST'])
def index():
    form = ViewForm()
    delete_view_form = DeleteViewForm()

    result = asyncio.run(get_hasura_connection(getMyViews))
    views = result['MyViews']
    show_cased_result = asyncio.run(get_hasura_connection(getFeaturedViews))
    featured_views = show_cased_result['Views']

    if request.method == "POST":
        data = request.form.to_dict()
        if delete_view_form.view_id.data and delete_view_form.validate_on_submit():
            params = {
                'id': data['view_id']
            }
            result = asyncio.run(get_hasura_connection_with_params(softDeleteMyView, params))
            view = result['UpdateMyViews']['returning']

            if view:
                views = [i for i in views if not (i['id'] == view[0]['id'])]
        elif form.title.data and form.validate_on_submit():
            data = request.form.to_dict()
            filename = secure_filename(form.graph_data.data.filename)
            if filename != '':
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
                    abort(400)
                else:
                    network_data = form.graph_data.data.stream.read().decode("utf-8")
                        # form.graph_data.json_blob
                    network_data = json.loads(network_data)

                    if network_data:
                        params = {
                            'title': data['title'],
                            'description': data['description'],
                            'node_label': data['node_label'],
                            'edge_label': data['edge_label'],
                        }
                        result = asyncio.run(get_hasura_connection_with_params(insertView, params))
                        view = result['InserViewsOne']

                        params = {
                            'view_id': view['id']
                        }
                        result = asyncio.run(get_hasura_connection_with_params(insertLayout, params))

                        # Define parentKey/parentLabel if nodes/edges not defined
                        # Example:
                        # {
                        #   "id": "nxpAPnATEb",
                        #   "name": "Obi-Wan Kenobi"
                        #   "homeworld": {
                        #     "id": "Fwz1bh8rSD",
                        #     "name": "Stewjon"
                        #   }
                        # }

                        if 'data' not in network_data[0].keys():
                            keys = ['id', 'attributes', 'filters']
                            parent_key = None
                            for item in network_data:
                                for key in item:
                                    if key not in keys and isinstance(item[key], dict):
                                        parent_key = key
                                        node_label = next(iter(item[key].keys() - set(keys)))
                                if parent_key:
                                    break

                            params = {
                                'view_id': view['id'],
                                'parent_key': parent_key,
                                'parent_label': node_label
                            }
                        else:
                            params = {
                                'view_id': view['id']
                            }
                        result = asyncio.run(get_hasura_connection_with_params(insertNode, params))
                        node = result['InsertNodesOne']

                        params = {
                            'view_id': view['id'],
                            'network_data': network_data,
                            'source': file_ext.replace('.', '')
                        }
                        result = asyncio.run(get_hasura_connection_with_params(insertDataOne, params))
                        data = result['InsertDataOne']

                        config = {
                            'data': data,
                            'node': node
                        }
                        params = {
                            'data_id': data['id'],
                            'transformed_network_data': load_elements(config)
                        }
                        asyncio.run(get_hasura_connection_with_params(updateDataById, params))

                        # nosemgrep:github.workflows.config.open-redirect
                        return redirect(request.url_root + current_app.config.get('DASH_URL_BASE') + view['id'])
    return render_template('index.html', title='Home', views=views, featured_views=featured_views, form=form,
                           delete_view_form=delete_view_form, dash_url_base=current_app.config.get('DASH_URL_BASE'))


@server_bp.app_context_processor
def utility_processor():
    query = getAuthenticatedUser
    result = asyncio.run(get_hasura_connection(query))
    user = result['atlas_authenticated_user'][0]
    return dict(user=user)


@server_bp.app_template_filter(name='datetime')
def format_timedelta(datetime_or_timedelta, granularity='second',
                     add_direction=False, threshold=0.85):
    """Format the elapsed time from the given date to now or the given
  timedelta.

  This function is also available in the template context as filter
  named `timedeltaformat`.
  """
    if isinstance(datetime_or_timedelta, datetime):
        datetime_or_timedelta = datetime.utcnow() - datetime_or_timedelta
    else:
        datetime_or_timedelta = datetime.strptime(datetime_or_timedelta, '%Y-%m-%dT%H:%M:%S.%f')
        datetime_or_timedelta = datetime.utcnow() - datetime_or_timedelta
    return babel.dates.format_timedelta(
        datetime_or_timedelta,
        granularity,
        threshold=threshold,
        add_direction=add_direction,
        locale='en_US'
    )
