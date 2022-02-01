import asyncio
import json
import re

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_cytoscape as cyto
import dash_html_components as html
import visdcc
from application.dashapp.styles import styles
from application.gql import get_hasura_connection, get_hasura_connection_with_params
from application.queries import getViewDetailsByID, getAuthenticatedUser
from flask import request, current_app
from flask.helpers import get_root_path

# Load extra layouts
cyto.load_extra_layouts()

with open(get_root_path(__name__) + '/styles/cy-style.json', 'r') as f:
    stylesheet = json.loads(f.read())

external_scripts = [{
    'src': 'https://cdn.rawgit.com/cytoscape/cytoscape.js-cose-bilkent/d810281d/cytoscape-cose-bilkent.js'
}]


# TODO: Need to set minZoom and maxZoom for all graphs (dropped from )
def render_layout():
    url = request.referrer
    if type(request.referrer) == str and 'dash_app_1' in request.referrer:
        url = request.referrer
    elif 'dash_app_1' in request.url:
        url = request.url
    else:
        return html.Div()

    view_id = re.findall(r"/dash_app_1/([A-Za-z0-9\-]+)", url)[0]

    if view_id is None:
        layout = ''
    else:
        query = getViewDetailsByID
        params = {
            'id': view_id
        }

        result = asyncio.run(get_hasura_connection_with_params(query, params))
        view_by_id = result['ViewsByID']

        view_by_id['ownerEmail']

        # Get authenticated user
        result = asyncio.run(get_hasura_connection(getAuthenticatedUser))
        isAdmin = result['atlas_authenticated_user'][0]['email'] == view_by_id['ownerEmail']

        layout_by_view_id = view_by_id['layout']
        data_by_view_id = view_by_id['data'][0]
        config = {
            "logo": {
                "file": "assets/images/Atlas_Logo_horizontal_full-color.svg",
                "link": request.url_root + current_app.config['SUBDIRECTORY'],
                "text": "IQT Labs"
            },
            "legend": {
                "nodeLabel": view_by_id['legendNodeLabel'],
                "edgeLabel": view_by_id['legendEdgeLabel']
            }
        }

        elements_ls = data_by_view_id['transformedNetworkData']

        node_dictionary = {}
        node_dictionary_by_label = {}
        labels = []
        for dic in elements_ls:
            if 'source' not in dic['data']:
                if dic['data']['label']:
                    node_dictionary[dic['data']['id']] = dic
                if dic['data']['label']:
                    node_dictionary_by_label[dic['data']['label']] = dic
                    if dic['data']['label'] not in labels:
                        labels.append(dic['data']['label'])

        # request graphql api for layout
        layout = html.Div(
            id='labs',
            style=styles['labs'],
            children=[
                dcc.Input(
                    id='url-anchor-tag',
                    type='hidden'
                ),
                dcc.Store(id='host', data=request.host),
                dcc.Store(id='data_id', data=data_by_view_id['id']),
                dcc.Store(id='layout_id', data=layout_by_view_id['id']),
                dcc.Store(id='layout_by_view_id', data=layout_by_view_id),
                dcc.Store(id='view_id', data=view_id),
                dcc.Store(id='is_admin', data=isAdmin),
                dcc.Store(id='elements_ls_store', data=elements_ls),
                dcc.Store(id='node_dictionary_store', data=node_dictionary),
                dcc.Store(id='labels_store', data=labels),
                dcc.Store(id='node_dictionary_by_label_store', data=node_dictionary_by_label),
                dcc.Location(id='url', refresh=False),
                html.Div(id='output'),

                html.Div(
                    id='adminpanel',
                    className='adminpanel',
                    style=styles['#adminpanel'],
                    children=[
                        html.Span('Image Type:', style=styles['#adminpanel .label']),
                        dcc.Dropdown(
                            id='dropdown-image-type',
                            style=styles['#adminpanel .dropdown'],
                            options=[
                                {'label': name.capitalize(), 'value': name}
                                for name in ['png', 'jpeg', 'svg']
                            ],
                            searchable=False,
                            clearable=False,
                            value='png',
                        ),
                        html.Div(
                            style=styles['#adminpanel .button'],
                            children=[
                                dbc.Button(
                                    html.Span(html.I(className="fa fa-camera"),
                                              id="download-screenshot-button",
                                              title="Download Screenshot"),
                                    color="primary", className="me-1",

                                )]
                        ),
                        html.Hr(),
                        html.Span('Layout Name:', style=styles['#adminpanel .label']),
                        dcc.Dropdown(
                            id='dropdown-update-layout',
                            style=styles['#adminpanel .dropdown'],
                            options=[
                                {'label': name.capitalize(), 'value': name}
                                for name in ['cose-bilkent', 'klay', 'grid', 'concentric', 'preset']
                            ],
                            searchable=False,
                            clearable=False,
                            value=layout_by_view_id['name'],
                        ),
                        html.Div(
                            style=styles['#save-layout-button'],
                            children=[
                                dbc.Button("Save Layout", id="save-layout-button", color="primary", className="me-1")
                            ]
                        ),

                    ],
                ),
                html.Div(id='fixed-admin-button',
                         className='fixed-admin-button',
                         style=styles['#fixed-admin-button'],
                         children=html.Span(html.I(className="fa fa-cog"),
                                            className="btn-floating btn-lg btn-secondary")
                         ),
                html.Div(id='main-panel',
                         className='main-panel',
                         children=html.Div(
                             className='col',
                             style=styles['mainpanel.col'],
                             children=([
                                 html.Div(
                                     children=html.A(
                                         href=config['logo']['link'],
                                         children=
                                         html.Img(
                                             className='main-image',
                                             src='assets/images/Atlas_Logo_horizontal_full-color.svg',
                                             alt=config['logo']['text']
                                         )
                                     ),
                                     className='main-title',
                                     style=styles['main-title'],
                                 ),
                                 html.Div(
                                     children=html.H2(
                                         children=view_by_id['title'],
                                         style=styles['mainpanel.h2']
                                     ),
                                     className='title',
                                     style=styles['title'],
                                 ),
                                 html.Div(
                                     children=view_by_id['description'],
                                     className='title-text',
                                     style=styles['title-text']
                                 ),
                                 html.Div(
                                     id='legend',
                                     children=html.Div(
                                         className="box",
                                         children=[
                                             html.H2(
                                                 children='Legend',
                                                 style=styles['mainpanel.h2']
                                             ),
                                             html.Dl(
                                                 style=dict(styles['mainpanel.dl'], **styles['dl']),
                                                 children=([
                                                     html.Dt(
                                                         className='node',
                                                         style=dict(styles['mainpanel.node'], **styles['mainpanel.dt'],
                                                                    **styles['dt'])
                                                     ),
                                                     html.Dd(
                                                         children=config['legend']['nodeLabel'],
                                                         style=dict(styles['legend.dd'], **styles['dd'])
                                                     ),
                                                     html.Dt(
                                                         className='edge',
                                                         style=dict(styles['mainpanel.edge'], **styles['mainpanel.dt'],
                                                                    **styles['dt'])
                                                     ),
                                                     html.Dd(
                                                         children=config['legend']['edgeLabel'],
                                                         style=dict(styles['legend.dd'], **styles['dd'])
                                                     )
                                                 ])
                                             )
                                         ]
                                     ),
                                 ),
                                 html.Div(
                                     children=html.Div(
                                         className='cf',
                                         style=dict(styles['search'], **styles['cf']),
                                         children=([
                                             html.H2(
                                                 children='Search',
                                                 style=styles['mainpanel.h2']
                                             ),
                                             dcc.Input(
                                                 id='search',
                                                 name='search',
                                                 type='text',
                                                 debounce=True,
                                                 placeholder='Enter a keyword',
                                                 className='empty',
                                                 style=dict(styles['#search input.empty'],
                                                            **styles['#search input[name="search"]']),
                                             ),
                                             html.Div(
                                                 id='search-button',
                                                 className='state searching',
                                                 style=styles['#search .state']
                                             ),
                                             visdcc.Run_js(id='add-hash-from-search'),
                                             visdcc.Run_js(id='save-element-positions'),
                                             visdcc.Run_js(id='save-graph-image'),
                                             visdcc.Run_js(id='save-layout-data'),
                                             html.Div(
                                                 id='search-results'
                                             )
                                         ])
                                     ),
                                     className='b1',
                                     style=styles['mainpanel.b1'],
                                 ),
                             ])
                         ),
                         style=styles['main-panel']
                         ),
                html.Div(
                    className='ui-settings',
                    style=styles['ui-settings'],
                    children=html.Button(
                        className='btn-open-options btn btn-warning',
                        style=dict(styles['btn-open-options'], **styles['btn'], **styles['btn-warning'],
                                   **styles['fa-2x'], **styles['fa-spin']),
                        children=html.I(
                            className='fa fa-cog fa-w-16 fa-spin fa-2x',
                            style=dict(styles['fa-2x'], **styles['fa-spin']),
                        ),
                    ),
                ),
                html.Div(
                    id='attributepane',
                    className='attributepane',
                    style=styles['#attributepane'],
                    children=html.Div(
                        className='text',
                        style=styles['#attributepane .text'],
                        children=([
                            html.Div(
                                id='close-attributepane',
                                className='left-close returntext',
                                style=styles['.left-close'],
                                title='Close',
                                children=html.Div(
                                    className='c cf',
                                    style=styles['cf'],
                                    children=html.Span(
                                        children='See all'
                                    )
                                ),
                            ),
                            html.Div(
                                className='headertext',
                                style=styles['#attributepane .headertext'],
                                children=html.Span(
                                    children='Details'
                                )
                            ),
                            html.Div(
                                id='nodeattributes'
                            ),
                        ])
                    )
                ),
                cyto.Cytoscape(
                    id='cytoscape',
                    elements=elements_ls,
                    responsive=True,
                    layout=layout_by_view_id,
                    stylesheet=stylesheet,
                    style={
                        'width': '70%',
                        'height': '100%',
                        'position': 'absolute',
                        'left': 300,
                        'top': 0,
                        'z-index': 999,
                    }
                )
            ])
    return layout
