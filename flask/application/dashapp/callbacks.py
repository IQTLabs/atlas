import asyncio
import base64
import os
import urllib

import dash
import dash_html_components as html
import validators
from application.dashapp.styles import styles
from application.gql import get_hasura_connection_with_params, get_headers
from application.queries import searchNetworkData
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from flask import current_app


def register_callbacks(dashapp):
    # nosemgrep:github.workflows.config.useless-inner-function
    @dashapp.callback(
        Output('save-graph-image', 'run'),
        [
            Input('cytoscape', 'imageData'),
            State('view_id', 'data'),
            State('is_admin', 'data')
        ]
    )
    def put_image_string(data, view_id, is_admin):
        """Decode and store a screenshot to filesystem, triggered automatically or when layout saved"""
        ctx = dash.callback_context
        # TODO: save once..
        if ctx.triggered:
            if is_admin:
                relative_file_name = 'static/images/' + view_id + '.png'
                file_name = 'flask/application/' + relative_file_name

                if os.getcwd() == '/flask':
                    file_name = '/' + file_name

                with open(file_name, 'wb') as fh:
                    # save image file in screenshots directory
                    fh.write(base64.b64decode(data.replace('data:image/png;base64,', '')))
                headers = get_headers()

                # save file location in database
                return '''
                    var cy = window.cy;
                    async function saveImageData() {{
                        const query = `
                            mutation saveImageData($view_id: uuid!, $image: String){{
                                UpdateMyViews(where: {{id: {{ _eq: $view_id }} }}, _set: {{image: $image}}) {{
                                    returning {{
                                        id
                                    }}
                                }}
                            }}
                        `
                        const variables = {{
                            'view_id': "{0}",
                            'image': "{1}"
                        }}
                        
                        const options = {{
                            'method': 'POST',
                            'headers': {{
                                'x-hasura-remote-user': '{2}',
                                'x-hasura-role': '{3}'
                            }},
                            'body': JSON.stringify( {{ query, variables }} )
                        }}
                        const res = await fetch('{4}', options )
                    }}
                    saveImageData();
                '''.format(view_id, relative_file_name,
                           headers['x-hasura-remote-user'],
                           headers['x-hasura-role'],
                           current_app.config.get('CLIENT_HASURA_GRAPHQL_API'))

    # Save image if user is graph owner
    # nosemgrep:github.workflows.config.useless-inner-function
    @dashapp.callback(
        Output("cytoscape", "generateImage"),
        [
            Input('download-screenshot-button', 'n_clicks'),
            Input('dropdown-image-type', 'value'),
            Input('save-layout-button', 'n_clicks'),
            State('is_admin', 'data')
        ])
    def get_image(download_button, image_type, save_layout_button, is_admin):
        # 'store': Stores the image data in 'imageData' !only jpg/png are supported
        # 'download'`: Downloads the image as a file with all data handling
        # 'both'`: Stores image data and downloads image as file.
        action = 'store'
        ctx = dash.callback_context
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger == 'download-screenshot-button' or trigger == 'dropdown-image-type':
            action = 'download'
        else:
            image_type = 'png'

        print(trigger, action)
        if trigger == 'download-screenshot-button' or trigger == '':
            return {
                'type': image_type,
                'action': action
            }
        if trigger == 'dropdown-image-type':
            raise PreventUpdate

    # nosemgrep:github.workflows.config.useless-inner-function
    @dashapp.callback(
        Output('cytoscape', 'elements'),
        [
            Input('cytoscape', 'tapNodeData'),
            Input('search-button', 'n_clicks'),
            Input('url', 'hash'),
            Input('close-attributepane', 'n_clicks'),
            Input('search-results', 'children')
        ],
        [
            State('cytoscape', 'elements'),
            State('elements_ls_store', 'data'),
            State('labels_store', 'data'),
            State('node_dictionary_by_label_store', 'data'),
            State('node_dictionary_store', 'data')
        ])
    def neighbor_elements(nodeData, n_clicks, url_hash, close_button, search_results, elements, elements_ls, labels,
                          node_dictionary_by_label, node_dictionary):
        ctx = dash.callback_context
        if ctx.triggered:
            trigger = ctx.triggered[0]['prop_id'].split('.')[0]
            print('   --   display cytoscape elements   --- ')

            if trigger == 'close-attributepane':
                return elements_ls

            if trigger == 'search-button' or trigger == 'search-results':
                nodeData = get_first_match(search_results, labels, node_dictionary_by_label)

            if trigger == 'url':
                url_hash = url_hash.replace('#', '')
                if url_hash:
                    nodeData = node_dictionary_by_label[urllib.parse.unquote(url_hash)]['data']
                else:
                    return elements_ls

            if nodeData:
                return get_neighbor_elements(nodeData, elements_ls, node_dictionary)

    # nosemgrep:github.workflows.config.useless-inner-function
    @dashapp.callback(
        Output('search-results', 'children'),
        [
            Input('search-button', 'n_clicks'),
            Input('search', 'value')],
        [
            State('search', 'value'),
            State('labels_store', 'data'),
            State('data_id', 'data')
        ])
    def display_search_results(search_button, search_value, search_term, labels, data_id):
        ctx = dash.callback_context
        if ctx.triggered:
            print('   --   display_search_results   --- ')
            trigger = ctx.triggered[0]['prop_id'].split('.')[0]

            if trigger == 'search-button' or trigger == 'search':
                params = {
                    'id': data_id,
                    'keyword': search_value
                }
                result = asyncio.run(get_hasura_connection_with_params(searchNetworkData, params))
                search_results = result['atlas_search_data_tsvector']
                results = []
                for x in search_results:
                    results.append(x['result'])
                lists = generate_anchor_list(results)

                return html.Div(
                    className="trend",
                    children=[
                        html.Div(
                            id='results',
                            className='results',
                            children=
                            html.P(
                                children=html.B(
                                    children='Search Results'
                                )
                            )
                        ),
                        html.Ul(
                            id='search-results-list',
                            style=styles['.list-style-none'],
                            children=lists
                        )
                    ],
                )
        else:
            return ''

    ## hash generated when viewing dashapp outside of flask
    # nosemgrep:github.workflows.config.useless-inner-function
    @dashapp.callback(
        Output('add-hash-from-search', 'run'),
        [
            Input('search-button', 'n_clicks'),
            Input('search', 'value'),
            Input('cytoscape', 'tapNodeData'),
            Input('close-attributepane', 'n_clicks'),
            Input('search-results', 'children'),
            Input('url', 'href'),
        ],
        [
            State('labels_store', 'data'),
            State('node_dictionary_by_label_store', 'data'),
            State('view_id', 'data'),
        ])
    def generate_anchor(search_button, search_value, nodeData, close_button, search_results, url_href, labels,
                        node_dictionary_by_label, view_id):
        ctx = dash.callback_context
        if ctx.triggered:
            print(' -----   generate_anchor  ------ ')
            trigger = ctx.triggered[0]['prop_id'].split('.')[0]

            if view_id in url_href:
                nodeLabel = ''
                if trigger == 'cytoscape':
                    nodeLabel = nodeData['label']

                if trigger == 'search-button' or trigger == 'search':
                    nodeData = get_first_match(search_results, labels, node_dictionary_by_label)
                    nodeLabel = nodeData['label']

                if trigger == 'close-attributepane':
                    nodeLabel = ''
                    return '''
                        var anchor = document.getElementById('url-anchor-tag');
                        console.log(anchor);
                        history.pushState(null, '', '#{}');
                    '''.format(nodeLabel, search_value)

                if (nodeLabel):
                    return '''
                        var anchor = document.getElementById('url-anchor-tag');
                        console.log(anchor);
                        history.pushState(null, '', '#{}');
                    '''.format(nodeLabel, search_value)
            else:
                return '''
                  window.location.reload(true);
            '''.format(url_href)

    # Admin button will only show up for graph owner
    # nosemgrep:github.workflows.config.useless-inner-function
    @dashapp.callback(
        Output('adminpanel', 'style'),
        [
            Input('fixed-admin-button', 'n_clicks'),
            Input('attributepane', 'style'),
        ],
        [
            State('adminpanel', 'style'),
            State('is_admin', 'data')
        ])
    def style_attribute_pane(admin_button, attribute_pane, original_styles, is_admin):
        ctx = dash.callback_context
        if ctx.triggered:
            trigger = ctx.triggered[0]['prop_id'].split('.')[0]
            if trigger == 'attributepane':
                if attribute_pane['visibility'] == 'visible':
                    styles['#adminpanel']['visibility'] = 'hidden'
            # elif is_admin:
            else:
                if styles['#adminpanel']['visibility'] == 'visible':
                    styles['#adminpanel']['visibility'] = 'hidden'
                else:
                    styles['#adminpanel']['visibility'] = 'visible'
        return styles['#adminpanel']

    # Save preset button will only show up for graph owner
    # nosemgrep:github.workflows.config.useless-inner-function
    @dashapp.callback(
        Output('save-element-positions', 'run'),
        [
            Input('save-layout-button', 'n_clicks'),
            Input('dropdown-update-layout', 'value'),
            State('data_id', 'data'),
            State('layout_id', 'data'),
            State('is_admin', 'data')
        ])
    def save_layout_name(admin_click, layout_name, data_id, layout_id, is_admin):
        ctx = dash.callback_context

        if ctx.triggered:
            trigger = ctx.triggered[0]['prop_id'].split('.')[0]
            if trigger == 'save-layout-button' and is_admin:
                # Owner is able to move his nodes around and save preset data
                headers = get_headers()

                return '''
                    var cy = window.cy
        
                    async function savePresetLayout() {{
                        const query = `
                            mutation setLayoutName($data_id: uuid!, $layout_id: uuid!, $transformedNetworkData: jsonb, $layout_name: String!){{
                                UpdateDataById(pk_columns: {{ id: $data_id }}, _set: {{ transformedNetworkData: $transformedNetworkData }}){{
                                    viewId
                                }}
                                UpdateLayoutById( pk_columns: {{ id: $layout_id }}, _set: {{ name: $layout_name }} ) {{
                                    id
                                }}
                            }}
                        `
                        let variables = {{
                            'data_id': "{0}",
                            'layout_id': "{1}",
                            'layout_name': "{5}",
                            'transformedNetworkData': cy.elements().jsons()
                        }}
                        
                        if ('{5}' != 'preset') {{
                            let cyElements = cy.elements().jsons()
                            for (var index in cyElements) {{
                                if (cyElements[index].hasOwnProperty('position')) {{
                                    delete cyElements[index]['position'];
                                }}
                            }}                        
                            variables['transformedNetworkData'] = cyElements
                        }}
                        
                        const options = {{
                            'method': 'POST',
                            'headers': {{
                                'x-hasura-remote-user': '{2}',
                                'x-hasura-role': '{3}',
                            }},
                            'body': JSON.stringify( {{ query, variables }} )
                        }}
                        
                        const res = await fetch( '{4}', options )
                        
                        function updateButton(text, color){{
                            button.innerHTML = text
                            button.style.backgroundColor = color;
                            button.style.borderColor = color;
                            setTimeout(function() {{
                                button.innerHTML = "Save Layout"
                                button.style.backgroundColor = '#2c3e50';
                                button.style.borderColor = '#2c3e50';
                            }}, 4000);
                        }}
                        
                        var button = document.getElementById("save-layout-button");
                        if (res.status == 200) {{
                            updateButton("Layout Saved", '#18bc9c');
                        }} else {{
                            updateButton("Error Saving Layout", '#e74c3c');
                        }}
                    }}
                    savePresetLayout();
                '''.format(data_id, layout_id,
                           headers['x-hasura-remote-user'],
                           headers['x-hasura-role'],
                           current_app.config.get('CLIENT_HASURA_GRAPHQL_API'),
                           layout_name)

    # nosemgrep
    @dashapp.callback(
        Output('cytoscape', 'layout'),
        [
            Input('dropdown-update-layout', 'value')
        ], [
            State('layout_by_view_id', 'data')
        ])
    def update_layout(layout_name, layout_data):
        layout_data['name'] = layout_name
        return layout_data

    # Save preset button will only show up for graph owner
    # nosemgrep:github.workflows.config.useless-inner-function
    @dashapp.callback(
        Output('save-layout-button', 'style'),
        [
            Input('adminpanel', 'style'),
            State('is_admin', 'data')
        ])
    def style_admin_button(adminpanel, is_admin):
        ctx = dash.callback_context
        if ctx.triggered:
            if adminpanel['visibility'] == 'visible' and is_admin:
                styles['#save-layout-button']['visibility'] = 'visible'
            else:
                styles['#save-layout-button']['visibility'] = 'hidden'
            return styles['#save-layout-button']

    # nosemgrep:github.workflows.config.useless-inner-function
    @dashapp.callback(
        Output('attributepane', 'style'),
        [
            Input('search-button', 'n_clicks'),
            Input('cytoscape', 'tapNodeData'),
            Input('close-attributepane', 'n_clicks'),
            Input('url', 'hash'),
            Input('search-results', 'children')
        ],
        [
            State('attributepane', 'style'),
            State('labels_store', 'data'),
            State('node_dictionary_by_label_store', 'data')
        ])
    def style_attribute_pane(search_button, nodeData, close_button, url_hash, search_results, original_styles, labels,
                             node_dictionary_by_label):
        ctx = dash.callback_context
        if ctx.triggered:
            print(' -----   display attribute pane  ------ ')
            trigger = ctx.triggered[0]['prop_id'].split('.')[0]

            nodeLabel = ''
            if trigger == 'cytoscape':
                nodeLabel = nodeData['label']

            if trigger == 'search-button' or trigger == 'search-results':
                nodeData = get_first_match(search_results, labels, node_dictionary_by_label)
                nodeLabel = nodeData['label']

            if trigger == 'url':
                url_hash = url_hash.replace('#', '')
                if url_hash:
                    nodeData = node_dictionary_by_label[urllib.parse.unquote(url_hash)]['data']
                    nodeLabel = nodeData['label']
                else:
                    styles['#attributepane']['visibility'] = 'hidden'
                    return styles['#attributepane']

            if nodeLabel:
                styles['#attributepane']['visibility'] = 'visible'
                return styles['#attributepane']
            else:
                styles['#attributepane']['visibility'] = 'hidden'
                return styles['#attributepane']

    # nosemgrep:github.workflows.config.useless-inner-function
    @dashapp.callback(
        Output('nodeattributes', 'children'),
        [
            Input('search-button', 'n_clicks'),
            Input('cytoscape', 'tapNodeData'),
            Input('close-attributepane', 'n_clicks'),
            Input('url', 'hash'),
            Input('search-results', 'children')
        ],
        [
            State('attributepane', 'style'),
            State('labels_store', 'data'),
            State('node_dictionary_by_label_store', 'data'),
            State('elements_ls_store', 'data'),
            State('node_dictionary_store', 'data'),
            State('host', 'data')
        ])
    def display_nodeattributes_children(search_button, nodeData, close_button, url_hash, search_results,
                                        original_styles, labels, node_dictionary_by_label, elements_ls, node_dictionary,
                                        host_name):
        ctx = dash.callback_context
        if ctx.triggered:
            print(' -----   nodeattributes children  ------ ')
            trigger = ctx.triggered[0]['prop_id'].split('.')[0]

            nodeLabel = ''
            if trigger == 'cytoscape':
                nodeLabel = nodeData['label']

            if trigger == 'search-button' or trigger == 'search-results':
                nodeData = get_first_match(search_results, labels, node_dictionary_by_label)
                nodeLabel = nodeData['label']

            if trigger == 'url':
                url_hash = url_hash.replace('#', '')
                if url_hash:
                    nodeData = node_dictionary_by_label[urllib.parse.unquote(url_hash)]['data']
                    nodeLabel = nodeData['label']

            if nodeLabel:
                nodeAttributes = []

                attributeName = html.P(
                    className='name',
                    children=nodeData['label']
                )
                nodeAttributes.append(attributeName)

                if 'attributes' in nodeData:
                    for key in nodeData['attributes']:
                        if 'image' in key.lower():
                            attributeImage = html.Img(
                                style=styles['#attributepane .image'],
                                src=nodeData['attributes'][key]
                            )
                            nodeAttributes.append(attributeImage)
                        elif 'link' in key.lower() and validators.url(nodeData['attributes'][key]):
                            if host_name in nodeData['attributes'][key]:
                                anchor_target = '';
                            else:
                                anchor_target = '_blank'
                            attributeLink = html.P(
                                className=key,
                                children=[
                                    html.B(
                                        children=key + ': '
                                    ),
                                    html.A(
                                        href=nodeData['attributes'][key],
                                        children=nodeData['attributes'][key],
                                        target=anchor_target
                                    ),
                                ]
                            )
                            nodeAttributes.append(attributeLink)
                        elif 'label' not in key:
                            attributeLead = html.P(
                                className=key + '9',
                                children=[
                                    html.B(
                                        children=key + ': '
                                    ),
                                    html.Span(
                                        children=nodeData['attributes'][key]
                                    ),
                                ]
                            )
                            nodeAttributes.append(attributeLead)

                neighbor_elements = get_neighbor_elements(nodeData, elements_ls, node_dictionary)
                connection_labels = []
                for i in neighbor_elements:
                    if 'source' not in i['data'] and i['data']['id'] != nodeData['id']:
                        connection_labels.append(i['data']['label'])
                connections = generate_anchor_list(connection_labels)

                return html.Div(
                    children=([
                        html.Div(
                            className='name',
                            style=styles['#attributepane .name'],
                            children=nodeAttributes
                        ),
                        html.Div(
                            className='data',
                        ),
                        html.Div(
                            className='p',
                            children='Connections:'
                        ),
                        html.Div(
                            className='link',
                            children=html.Ul(
                                children=connections,
                                id='search-results-list',
                                style=styles['.list-style-none']
                            )
                        ),
                    ]),
                    className='nodeattributes'
                )


def get_first_match(search_results, labels, node_dictionary_by_label):
    first_match = search_results['props']['children'][1]['props']['children'][0]['props']['children'][0]['props'][
        'children']
    return node_dictionary_by_label[first_match]['data']


def get_neighbor_elements(nodeData, elements_ls, node_dictionary):
    if nodeData:
        neighbor_elements = []
        for dic in elements_ls:
            # get edges
            if 'source' in dic['data']:
                if nodeData['id'] in dic['data']['source']:
                    neighbor_elements.append(dic)
                    neighbor_elements.append(node_dictionary.get(dic['data']['target']))
                if nodeData['id'] in dic['data']['target']:
                    neighbor_elements.append(dic)
                    neighbor_elements.append(node_dictionary.get(dic['data']['source']))
            else:
                # get nodes
                if nodeData['id'] in dic['data']['id']:
                    neighbor_elements.append(dic)

        return neighbor_elements


def generate_anchor_list(items):
    html_list = []
    count = 0
    for i in items:
        anchor = '#' + i
        count = count + 1
        html_list.append(html.Li(
            children=[
                html.A(
                    id={
                        'type': 'filter-anchor',
                        'index': i
                    },
                    href=anchor,
                    children=i
                )
            ]
        ))
    return html_list
