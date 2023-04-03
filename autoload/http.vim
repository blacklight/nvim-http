if has("python3") == 1
    let s:plugin_root_dir = fnamemodify(resolve(expand('<sfile>:p')), ':h')

python3 << EOF
import sys
from os.path import normpath, join
import vim

plugin_root_dir = vim.eval('s:plugin_root_dir')
src = join(plugin_root_dir, '..', 'python')
python_root_dir = normpath(join(plugin_root_dir, '..', 'python'))
deps = [src]
sys.path[0:0] = deps

import nvim_http
EOF

    function! http#Run()
        python3 nvim_http.run()
    endfunction

    function! http#Stop()
        python3 nvim_http.stop()
    endfunction
else
    echoerr 'nvim-http requires the Python extension installed'
endif

