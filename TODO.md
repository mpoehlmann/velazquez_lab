# TODO
- Legend outline
- ECSA file output, clean ecsa.py







# sandbox.py
Add storage for uploaded files


# Download
```python
html.Button("Download CSV", id="btn_csv"),
dcc.Download(id="download-dataframe-csv"),

df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [2, 1, 5, 6], "c": ["x", "x", "y", "y"]})
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(df.to_csv, "mydf.csv")
    return dcc.send_file("./dash_docs/assets/images/gallery/dash-community-components.png")
```