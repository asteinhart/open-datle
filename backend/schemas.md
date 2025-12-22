USERS

- user_id: int
- email: str
-

USER_DATA_LINE

- user_id: int
- dataset_id: int
- user_line: [{x:str|int, y: int}, {x:str|int, y: int}]

SCHEDULE

- day: str
- dataset_id: int

DATASET

- dataset_id: int
- title: str
- x_axis_label: str
- y_axis_label: str
- data_id : [{x:str|int, y: int}, {x:str|int, y: int}] | [{borough: int, borough: int} ]
- type: "line" | "order"
- source: str (url? nyc id?)
