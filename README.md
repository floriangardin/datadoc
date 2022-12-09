Datadoc
=======

Parse a datascience code file and export the processing to Kedro.

Simple use case :

- Only supports pd.read_\*(\*) operations as inputs
- Only supports .to_\*(\*) as outputs


Setup
-----

Go in the project root directory :
```
pip install .
```
Now you can use datadoc CLI !


Use CLI
-------

```
datadoc --node_name <node_name> --input_path <input_path> --kedro_path <kedro path>
```

- *node_name* : Name of the transformation (in one word)
- *input_path* : Code filepath you want to parse and export to kedro
- *kedro_path* : Kedro project directory


Example
-------

Input code : 

```python
# code.py
import pandas as pd

sales = pd.read_csv('sales.csv')
other_sales = pd.read_excel('other_sales.xlsx')

total_sales = sales - other_sales
total_sales.to_csv('total_sales.csv')

```

```bash
datadoc --node_name get_total_sales --input_path code.py --kedro_path ../kedro_project/
```

Result : 

```python
# ../kedro_project/src/kedro_project/pipelines/nodes.py

def get_total_sales(sales, other_sales):
	total_sales_charlotte = sales - other_sales
	return total_sales_charlotte, 

# ../kedro_project/src/kedro_project/pipelines/pipeline.py

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import get_total_sales

def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=get_total_sales,
                inputs=["sales", "other_sales"],
                outputs=["total_sales"],
                name="get_total_sales",
            )
        ]
    )


```