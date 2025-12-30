import lancedb
import pandas as pd
# uri = "default-text_unit-text"
uri = "./"
db = lancedb.connect(uri)

table = db.open_table("default-text_unit-text")
df = table.to_pandas()
# >>> df.columns
# Index(['id', 'text', 'vector', 'attributes'], dtype='object')

print(df.index)
