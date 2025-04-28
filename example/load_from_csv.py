from fukinotou import CsvLoader, CsvLoaded, LoadingException
from pydantic import BaseModel
import polars
import pandas


class User(BaseModel):
   id: int
   name: str
   age: int


try:
   users: CsvLoaded[User] = CsvLoader(User).load("./users.csv")
   print(users)
   print(users.value[1].value.name)
except LoadingException as e:
   print(f"Failed to load: {e}")

users_dataframe = users.to_polars(include_path_as_column=True)
print(users_dataframe)

