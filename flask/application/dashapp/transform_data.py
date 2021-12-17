import uuid

# Transform data and define elements
def transform_data(data_dict, config):
    transformed_data = []
    rootKey = config['node']['parentKey']
    label = config['node']['parentLabel']

    # NODES
    for n in data_dict:
        json_object = {
            'data': {
                'id': n['id'],
                'label': n[label]
            }
        }
        if n[rootKey]:
            json_object['data']['parentId'] = n[rootKey]['id']
        if 'attributes' in n:
            json_object['data']['attributes'] = n['attributes']
        if 'filters' in n:
            json_object['data']['filters'] = n['filters']
        transformed_data.append(json_object)

    for n in data_dict:
        if n[rootKey] is None:
            json_object = {
                'data': {
                    'id': n['id'],
                    'label': n[label],
                }
            }
            matches = next((item for item in transformed_data if item['data']['id'] == json_object['data']['id']), None)
        else:
            json_object = {
                'data': {
                    'id': n[rootKey]['id'],
                    'label': n[rootKey][label],
                }
            }
            if 'attributes' in n[rootKey]:
                json_object['data']['attributes'] = n[rootKey]['attributes']
            if 'filters' in n[rootKey]:
                json_object['data']['filters'] = n[rootKey]['filters']
            matches = next((item for item in transformed_data if item['data']['id'] == json_object['data']['id']), None)

        if matches is None:
            transformed_data.append(json_object)

    # EDGES
    for n in data_dict:
        if n[rootKey]:
            json_object = {
                'data': {
                    'source': n['id'],
                    'target': n[rootKey]['id'],
                    'id': str(uuid.uuid4()),
                }
            }
            transformed_data.append(json_object)

    return transformed_data
