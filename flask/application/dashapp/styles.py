styles = {
    'container': {
        'position': 'fixed',
        'display': 'flex',
        'flex-direction': 'column',
        'height': '100%',
        'width': '100%',
        'line-height': '1.25em'
        
    },
    'main-panel': {
      'margin-top': '50px',
      'margin-left': '25px',
      'background': '#fff',
      'border-radius': '10px',
      'box-shadow': '0 3px 10px rgb(0 0 0 / 20%)',
      'background-color': 'rgba(255, 255, 255, 0.8)',
      'z-index': '20',
      'position': 'fixed',
      'top': 0
    },
    'mainpanel.col': {
        'display': 'flex',
        'flex-direction': 'column',
        'width': '240px',
        'padding': '18px 18px 18px 18px',
        'margin': 0
    },
    'main-title': {
        'margin-right': '10px',
    },
    'main-img-button': {
        'color': 'red',
        'align-self': 'flex-end',
    },
    '#fixed-admin-button': {
        'position': 'fixed',
        'right': '35px',
        'bottom': '35px',
        'z-index': '998',
        'margin-bottom': '0',
        'overflow': 'hidden',
        # 'display': '-webkit-box',
        # 'display': '-ms-flexbox',
        'display': 'flex',
        # '-webkit-box-align': 'end',
        # '-ms-flex-align': 'end',
        'align-items': 'flex-end',
        'padding': '15px 15px 15px 15px',
        'padding-bottom': '15px',
        'padding-left': '15px',
        'padding-right': '15px'
    },
    '#adminpanel': {
      'position': 'fixed',
      'bottom': '100px',
      'height': '310px',
      'width': '200px',
      'right': '45px',
      'background': '#fff',
      'border-radius': '10px',
      'box-shadow': '0 3px 10px rgb(0 0 0 / 20%)',
      'background-color': 'rgba(255, 255, 255, 0.8)',
      'z-index': '200',
      'display': 'flex',
      'flex-direction': 'column',
      'visibility': 'hidden',
      'padding': '20px'
    },
    '#adminpanel .dropdown': {
      'self-align': 'center',
      'margin-bottom': '5px'
    },
    '#adminpanel .button': {
      'align-self': 'flex-end',
    },
    '#save-layout-button': {
        'align-self': 'flex-end',
    },
    '#adminpanel .label': {
        'padding-bottom': '10px',
        'font-size': '17px',
        'font-weight': '700'
    },
    'main-image': {
        'padding': '0px',
        'margin': '0px'
    },
    'title': {
        'font-weight': 'bold',
        'overflow-wrap': 'normal'
    },
    'mainpanel.h2': {
        'padding-bottom': '10px',
        'font-size': '17px',
        'font-weight': '700'
    },
    'title-text': {
        'padding': '6px 0 10px 0',
        'overflow-wrap': 'wrap'
    },
    'cf': {
        'zoom': 1,
        'margin-left': '10px'
    },
    'mainpanel.more-information': {
        'background': 'url(assets/images/info-solid.svg)',
        'background-repeat': 'no-repeat',
        'margin-left': '5px'
    },
    'mainpanel.node': {
        'background-position': '-11px -119px',
        'background-repeat': 'no-repeat',
        'background-image': 'url(assets/images/sprite.png)'
    },
    'mainpanel.edge': {
        'background-position': '-51px -122px',
        'background-repeat': 'no-repeat',
        'background-image': 'url(assets/images/sprite.png)'
    },
    'line': {
        'font-size': '12px',
        'color': '#000',
        'text-decoration': 'none',
        'font-weight': 'bold',
        'cursor': 'pointer'
    },
    'legend.dd': {
        'margin-bottom': '8px',
        'color': '#000'
    },
    'mainpanel.dt': {
        'width': '20px',
        'height': '20px',
        'float': 'left'
    },
    'mainpanel.dl': {
        'padding-bottom': '10px'
    },
    'dl': {
        'display': 'block',
        'margin-block-start': '1em',
        'margin-block-end': '1em',
        'margin-inline-start': '0px',
        'margin-inline-end': '0px'
    },
    'dt': {
        'display': 'block'
    },
    'dd': {
        'display': 'block',
        'margin-inline-start': '40px'
    },
    'mainpanel.b1': {
        'padding': '0px 0 0 0'
    },
    'search': {
        'border-top': '1px solid #999',
        'font-size': '16px',
        'padding': '20px 0 0px 2px'
    },
    '#search input.empty': {
        'color': '#000'
    },
    '#search input[name="search"]': {
        'border': '1px solid #999',
        'background-color': '#fff',
        'padding': '5px 7px 4px 7px',
        'width': '177px',
        'color': '#000'
    },
    '#search .state.searching': {
        'background-position': '-11px -13px'
    },
    '#search .state': {
        'width': '14px',
        'height': '14px',
        'background-image': 'url(assets/images/sprite.png)',
        'float': 'right',
        'margin-top': '10px',
        'cursor': 'pointer',
        'background-position': '-131px -13px'
    },
    '#search .results b': {
        'padding-left': '2px'
    },
    '.list-style-none': {
        'list-style': 'none'
    },
    '#admin-button': {
        'visibility': 'hidden',
        'transition': '0.3s',
        'position': 'fixed',
        'bottom': '35px',
        'right': '35px',
        'display': 'flex',
        'justify-content': 'center',
        'align-items': 'center',
        'z-index': '10001',
        'background-color': '#119dff',
        'border-radius': '3%',
        'cursor': 'pointer',
        'color': '#ffffff'
    },
    '#attributepane': {
        'position': 'absolute',
        'height': 'auto',
        'bottom': '0px',
        'top': '0px',
        'right': '0px',
        'width': '240px',
        'overflow-wrap': 'normal',
        'background-color': 'rgba(255, 255, 255, 0.8)',
        'zIndex': 20,
        'margin': 0,
        'border-left': '1px solid #ccc',
        'padding': '0px 18px 0px 18px',
        'visibility': 'visible'
    },
    '#attributepane .text': {
        'height': '100%'
    },
    '#attributepane .image': {
        'vertical-align': 'middle',
        'width': '220px'
    },
    '#attributepane .name': {
        'font-size': '18px',
        'cursor': 'default',
        'padding-bottom': '10px',
        'padding-top': '18px',
        'font-weight': 'bold'
    },
    '.left-close': {
        'background-image': 'url(assets/images/fancybox_sprite.png)',
        'margin-left': '-37px',
        'z-index': 99999,
        'cursor': 'pointer',
        'padding-left': '31px',
        'line-height': '36px',
        'background-repeat': 'no-repeat',
        'margin-bottom': '25px',
        'font-weight': 'bold',
        'font-size': '14px'
    },
    '#attributepane .headertext': {
        'color': '#000',
        'margin-bottom': '5px',
        'height': '25px',
        'border-bottom': '1px solid #999',
        'padding': '0px 0 10px 0',
        'font-size': '16px',
        'font-weight': 'bold'
    },
    'labs': {
      'font-family': 'Assistant-Light, sans-serif'
    },
    'ui-settings': {
        'position': 'fixed',
        'zIndex': '155',
        'right': '-30px',
        'top': '0',
        'height': '100vh',
        'transform': 'translate(500px)',
        'transition': 'all .2s',
        'boxShadow': '-0.46875rem 0 2.1875rem rgb(4 9 20 / 3%), -0.9375rem 0 1.40625rem rgb(4 9 20 / 3%), -0.25rem 0 0.53125rem rgb(4 9 20 / 5%), -0.125rem 0 0.1875rem rgb(4 9 20 / 3%)'
    },
    'btn-open-options': {
        'borderRadius': '50px',
        'position': 'absolute',
        'left': '-114px',
        'bottom': '80px',
        'padding': '0',
        'height': '54px',
        'lineHeight': '54px',
        'width': '54px',
        'textAlign': 'center',
        'display': 'block',
        'boxShadow': '0 0.46875rem 2.1875rem rgb(4 9 20 / 3%), 0 0.9375rem 1.40625rem rgb(4 9 20 / 3%), 0 0.25rem 0.53125rem rgb(4 9 20 / 5%), 0 0.125rem 0.1875rem rgb(4 9 20 / 3%)',
        'marginTop': '-27px'
    },
    'btn': {
       'position': 'relative',
        'transition': 'color 0.15s,background-color 0.15s,border-color 0.15s,box-shadow 0.15s',
   
        'fontWeight': '500'
    },
    'btn-warning': {
        'color': '#212529',
        'backgroundColor': '#f7b924',
        'borderColor': '#f7b924'
    },
    'fa-2x': {
        'lineHeight': '2',
        'fontSize': '2em'
    },
    'fa-spin': {
        'animation': 'fa-spin 2s infinite linear'
    },
    'output': {
        'overflow-y': 'scroll',
        'overflow-wrap': 'break-word',
        'height': '50px',
        'border': 'thin lightgrey solid'
    },
    'tab': {
        'height': 'calc(18vh - 5px)'
    },

}
