const fs = require('fs');
fs.mkdirSync('hub/core/static/core/vendor', {recursive:true});
fs.copyFileSync('node_modules/htmx.org/dist/htmx.min.js', 'hub/core/static/core/vendor/htmx.min.js');
fs.copyFileSync('node_modules/htmx.org/LICENSE', 'hub/core/static/core/vendor/HTMX-LICENSE');
