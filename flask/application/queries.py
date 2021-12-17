from gql import gql

getAuthenticatedUser = gql("""
  query getAuthenticatedUser {
    atlas_authenticated_user {
      email
    }
  }
""")

# atlas.views
getViewByID = gql("""
  query getViewByID($id: uuid!) {
    ViewsByID(id: $id) {
      id
      title
      updatedAt
    }
  }
""")

getMyViews = gql("""
  query getMyViews {
    MyViews(order_by: {updatedAt: desc}, where: {isFeatured: {_eq: false}}) {
      id
      title
      description
      updatedAt
      image
      isFeatured
      ownerEmail
      layout {
        name
      }
    }
  }
""")

getFeaturedViews = gql("""
  query getFeaturedViews {
    Views(order_by: {updatedAt: desc}, where: {isFeatured: {_eq: true}}) {
      id
      title
      description
      updatedAt
      image
      isFeatured
      ownerEmail
      layout {
        name
      }
    }
  }
""")

getViewDetailsByID = gql("""
  query getViewByID($id: uuid!) {
    ViewsByID(id: $id) {
      id
      ownerEmail
      title
      description
      updatedAt
      legendNodeLabel
      legendEdgeLabel
      layout {
        animate
        animationDuration
        edgeElasticity
        fit
        gravity
        gravityCompound
        gravityRange
        gravityRangeCompound
        id
        idealEdgeLength
        initialEnergyOnIncremental
        name
        nestingFactor
        nodeDimensionsIncludeLabels
        nodeRepulsion
        numIter
        padding
        quality
        panningEnabled
        randomize
        refresh
        tile
        tilingPaddingHorizontal
        tilingPaddingVertical
        updatedAt
        userPanningEnabled
        userZoomingEnabled
        zoom
        zoomingEnabled
      }
      data(limit: 1, order_by: {updatedAt: desc}) {
        id
        source
        networkData
        transformedNetworkData
      }
      node {
        parentKey
        parentLabel
        sizesChildDescendants
        sizesRootChild
        sizesRoots
        fontSize
      }
    }
  }
""")

insertView = gql("""
  mutation insertView($title: String!, $description: String!, $node_label: String!, $edge_label: String!) {
    InserViewsOne(object: {title: $title, description: $description, legendNodeLabel: $node_label, legendEdgeLabel: $edge_label}) {
      id
    }
  }
""")

softDeleteMyView = gql("""
  mutation softDeleteMyView($id: uuid!) {
    UpdateMyViews(where: {id: {_eq: $id}}, _set: {deletedAt: "now()"}) {
      returning {
        id
        deletedAt
      }
    }
  }
""")

# atlas.layouts
getLayoutByViewID = gql("""
  query getLayoutByViewID($view_id: uuid!) {
    Layouts(where: {viewId: {_eq: $view_id}}) {
      animate
      animationDuration
      edgeElasticity
      fit
      gravity
      gravityCompound
      gravityRange
      gravityRangeCompound
      id
      idealEdgeLength
      initialEnergyOnIncremental
      name
      nestingFactor
      nodeDimensionsIncludeLabels
      nodeRepulsion
      numIter
      padding
      quality
      panningEnabled
      randomize
      refresh
      tile
      tilingPaddingHorizontal
      tilingPaddingVertical
      updatedAt
      userPanningEnabled
      userZoomingEnabled
      zoom
      zoomingEnabled
    }
  }
""")

insertLayout = gql("""
  mutation insertLayout($view_id: uuid!) {
    InsertLayoutsOne(object: {viewId: $view_id}) {
      id
    }
  }
""")

# atlas.nodes
insertNode = gql("""
  mutation InsertNodesOne($view_id: uuid!, $parent_key: String, $parent_label: String) {
    InsertNodesOne(object: {viewId: $view_id, parentKey: $parent_key, parentLabel: $parent_label}) {
      id
      parentKey
      parentLabel
      sizesChildDescendants
      sizesRootChild
      sizesRoots
      fontSize
    }
  }
""")

# atlas.data
insertDataOne = gql("""
  mutation insertDataOne($view_id: uuid!, $network_data: jsonb, $source: String) {
    InsertDataOne(object: {viewId: $view_id, networkData: $network_data, source: $source}) {
      id
      source
      networkData
    }
  }
""")

updateDataById = gql("""
  mutation UpdateDataById($data_id: uuid!, $transformed_network_data: jsonb) {
    UpdateDataById(pk_columns: {id: $data_id}, _set: {transformedNetworkData: $transformed_network_data}) {
      id
    }
  }
""")

searchNetworkData = gql("""
  query searchNetworkData($id: uuid!, $keyword: String!) {
    atlas_search_data_tsvector(args: {data_id: $id, keyword: $keyword}) {
      result
    }
  }
""")