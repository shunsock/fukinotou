from fukinotou import CsvLoaded, CsvLoader, LoadingException
from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    age: int


try:
    users: CsvLoaded[User] = CsvLoader(User).load("./users__invalid.csv")
except LoadingException as e:
    print(f"Failed to load: {e}")

# OUTPUT: age type must be str
# Failed to load: Validation Error: details Error reading file users__invalid.csv: Validation Error: details Error parsing row 3 in users__invalid.csv: 1 validation error for User
# age
#  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='二十四', input_type=str]
