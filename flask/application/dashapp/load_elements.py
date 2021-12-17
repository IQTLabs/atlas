import uuid

import numpy as np
import pandas as pd
import random2
import requests
from application.dashapp.transform_data import transform_data


def load_elements(config):
    HEX_PALETTE = ['#130047', '#027bfc', '#00acf1', '#f75040', '#a8aebc', '#7dc53e', '#8bc535', '#fbd300']

    if config['data']['source'] == 'json':
        elements_ls = config['data']['networkData']

        ### transform data if json needs nodes/edges defined
        if config['node']['parentKey']:
            elements_ls = transform_data(elements_ls, config)

    if config['data']['source'] == 'xlsx':
        ## Load xlsx file
        xl = pd.ExcelFile(config['data']['location'])
        column = xl.parse(xl.sheet_names[0])

        root_label = config['node']['parent']
        root_id = root_label.lower().replace(' ', '') + 'centralnode'

        json_object = {
            'data': {
                'id': root_id,
                'label': root_label,
            }
        }
        transformed_data = []
        transformed_data.append(json_object)

        children = column['What is the primary theme or category you would associate with this project?']
        secondary_theme_column = column[
            'What is the secondary theme or category you would associate with this project?']
        secondary_theme_column_dropna = secondary_theme_column.dropna()  # remove NaN values from a Pandas Series
        children = children.append(secondary_theme_column_dropna, ignore_index=True)

        themes = np.unique(np.array(children))

        for idx, theme in enumerate(themes):
            json_object = {
                'data': {
                    'id': 'theme' + theme.lower().replace(' ', ''),
                    'label': theme,
                    'parentId': root_id
                }
            }
            transformed_data.append(json_object)
            json_object = {
                'data': {
                    'source': 'theme' + theme.lower().replace(' ', ''),
                    'target': root_id,
                    'id': str(uuid.uuid4())
                }
            }
            transformed_data.append(json_object)

        projects = np.array(column['What is the name of your project?'])

        for idx, project in enumerate(projects):
            json_object = {
                'data': {
                    'id': 'project' + project.lower().replace(' ', ''),
                    'label': project,
                    'parentId': 'theme' + children[idx].lower().replace(' ', '')
                }
            }
            transformed_data.append(json_object)

            json_object = {
                'data': {
                    'source': 'theme' + children[idx].lower().replace(' ', ''),
                    'target': 'project' + project.lower().replace(' ', ''),
                    'id': str(uuid.uuid4())
                }
            }
            transformed_data.append(json_object)

        secondary_themes = np.array(secondary_theme_column)
        for idx, project in enumerate(projects):
            if isinstance(secondary_themes[idx], str):
                json_object = {
                    'data': {
                        'source': 'theme' + secondary_themes[idx].lower().replace(' ', ''),
                        'target': 'project' + project.lower().replace(' ', ''),
                        'id': str(uuid.uuid4())

                    }
                }
            transformed_data.append(json_object)

        elements_ls = transformed_data

    if config['data']['source'] == 'api':
        ### GRAPHQL API REQUEST
        query = config['data']['api']['query']
        url = config['data']['api']['url']
        headers = config['data']['api']['headers']
        response = requests.post(url, headers=headers, json={'query': query})

        ### Get data
        data_dict = response.json().get('data')
        queryObject = config['data']['api']['queryObject']
        queryObject = queryObject.split('.')

        for n in queryObject:
            data_dict = data_dict.get(n)

        ### TRANSFORM DATA: create dictionary of nodes/edges
        elements_ls = transform_data(data_dict, config)

    colors = {}
    roots = {}

    def random_color(hex_palette):
        if not len(hex_palette):
            hex_palette = list(HEX_PALETTE)
        random_choice = random2.choice(hex_palette)
        hex_palette.remove(random_choice)
        return random_choice

    # find roots
    for n in elements_ls:
        for k, v in list(n.items()):
            if 'label' in v and 'parentId' not in v:
                roots[n['data']['id']] = n['data']['label']

    # count root children to get palette size
    # children and grandchildren nodes/edges are grouped by color
    palette_size = 1 + len(roots)
    for n in elements_ls:
        for k, v in list(n.items()):
            if 'parentId' in v and v['parentId'] in roots:
                palette_size = palette_size + 1

    # atlas defined color palette
    hex_palette = list(HEX_PALETTE)

    # find root indices and set root styles
    root_indexer = dict((p['data']["id"], i) for i, p in enumerate(elements_ls))
    for n in roots:
        root_index = root_indexer.get(n, -1)
        elements_ls[root_index]['data']['size'] = config['node']['sizesRoots']
        elements_ls[root_index]['data']['fontSize'] = config['node']['fontSize']
        elements_ls[root_index]['data']['classes'] = 'center-right'
        elements_ls[root_index]['data']['color'] = random_color(hex_palette)  # '#F75040'

    # set styling on root children
    for n in elements_ls:
        for k, v in list(n.items()):
            if 'parentId' in v and v['parentId'] in roots:
                colors[n['data']['id']] = random_color(hex_palette)
                n['classes'] = 'center-right'
                n['data']['size'] = config['node']['sizesRootChild']
                n['data']['fontSize'] = config['node']['fontSize']
                n['data']['color'] = colors[n['data']['id']]
                n['group'] = 'nodes'
            elif 'source' in v:
                if v['source'] in roots or v['target'] in roots:
                    n['data']['width'] = 4.5
                else:
                    n['data']['width'] = 2.5

    def find_parent(elements_ls, x):
        index = root_indexer.get(x, -1)
        if 'color' in elements_ls[index]['data']:
            colors[x] = elements_ls[index]['data']['color']
            return elements_ls[index]['data']['color']
        else:
            return find_parent(elements_ls, elements_ls[index]['data']['parentId'])

    # set styling on descendants of children
    # need to remove elements once found..to make this faster
    for n in elements_ls:
        for k, v in list(n.items()):
            if 'parentId' in v and v['parentId'] not in roots:
                n['classes'] = 'center-right'
                n['data']['size'] = config['node']['sizesChildDescendants']
                n['data']['fontSize'] = config['node']['fontSize']
                if v['parentId'] in colors:
                    n['data']['color'] = colors[n['data']['parentId']]
                elif v['parentId'] not in colors:
                    n['data']['color'] = find_parent(elements_ls, v['parentId'])
                    # colors[v['parentId']] = n['data']['color']
            elif 'source' in v:
                n['classes'] = 'multi-unbundled-bezier'
                if v['source'] in colors:
                    n['data']['color'] = colors[v['source']]
                else:
                    n['data']['color'] = find_parent(elements_ls, v['source'])
    return elements_ls
