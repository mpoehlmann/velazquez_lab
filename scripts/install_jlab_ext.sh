#!/bin/bash

#-------------------------------------------------------------------
# This script installs an opinionated list of Jupyterlab extensions (updated 2021/05/12)
#
# LSP:
#   pip install jupyter-lsp
#   conda install python-language-server
#-------------------------------------------------------------------

LAB_EXTENSIONS=(
  "@jupyterlab/celltags"
  "@jupyter-widgets/jupyterlab-manager"
  "@jupyterlab/commenting-extension"
  "@jupyterlab/toc"
  "@ijmbarr/jupyterlab_spellchecker"
  "jupyterlab-plotly"
  "@j123npm/jupyterlab-dash"
  "plotlywidget@4.9.0"
  "jupyterlab-drawio"
  "@aquirdturtle/collapsible_headings"
  # "@ryantam626/jupyterlab_sublime"
  # # "dask-labextension"
  # "@bokeh/jupyter_bokeh"
  # # "@krassowski/jupyterlab-lsp"
  # "jupyterlab-system-monitor"
  # "jupyterlab-topbar-extension"
  "jupyterlab-theme-toggle"
  # # "@osscar/appmode-jupyterlab"
  # "jupyter-vuetify"
  # "ipycanvas"
)

for i in ${!LAB_EXTENSIONS[@]}; do
  echo "...installing extension: ${LAB_EXTENSIONS[$i]}"
  jupyter labextension install ${LAB_EXTENSIONS[$i]} --no-build
done

echo "...building jupyterlab"
jupyter lab build
