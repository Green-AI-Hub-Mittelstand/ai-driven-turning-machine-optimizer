# Database

The database is set up using PostgreSQL. The available scripts can be used to load data into the database or retrieve data from it.

## Usage

To work with the database, start by adjusting the `config.json` file. The scripts can then be used within your own classes:

**Read data:**

```python
from get_data_from_database import read_from_database

query = "SELECT * FROM 'Table';"

df = read_from_database(query)
```

**Write data:**

```python
from load_data_into_database import write_to_database

data = pd.read_csv("./Testdaten/Messungen.csv")

table_name = 'Messungen'

write_to_database(data, table_name)
```

You can store your own database in the `Backup` folder. It can then be automatically loaded into PostgreSQL using the provided batch file *(TODO: link to file)*.
