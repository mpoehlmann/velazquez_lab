# Linking Python with Microsoft Excel

## Setup
1. Enable ``Trust access to the VBA project object model`` under
``File > Options > Trust Center > Trust Center Settings > Macro Settings``.

2. Install the add-in via command prompt:
```bash
xlwings addin install
```

## Register Python function
```bash
xlwings quickstart excel_gc_conc.py
```