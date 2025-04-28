from fukinotou import JsonLoader, JsonLoaded, JsonsLoader, JsonsLoaded, LoadingException
from pydantic import BaseModel
import polars
import pandas


class User(BaseModel):
    id: int
    name: str
    age: int


try:
    user1: JsonLoaded[User] = JsonLoader(User).load("./user1.json")
    print(user1)
except LoadingException as e:
    print(f"Failed to load user1: {e}")

try:
    users: JsonsLoaded[User] = JsonsLoader(User).load("./")
    print(users)
except LoadingException as e:
    print(f"Failed to load users: {e}")

users_pandas_dataframe = users.to_pandas()
print(users_pandas_dataframe)
users_polars_dataframe = users.to_polars(include_path_as_column=True)
print(users_polars_dataframe)
