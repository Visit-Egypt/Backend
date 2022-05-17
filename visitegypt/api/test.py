from pydantic import BaseModel
import json
class Op(BaseModel):
    pass
import csv

start_hrs = []
end_hrs = []
with open('/home/geekahmed/Desktop/nb.csv', newline='') as f:
    csv_reader = csv.reader(f, delimiter=',')
    for line in csv_reader:
        start_hrs.append(line[0])
        end_hrs.append(line[1])

start_hrs.remove("FROM")
end_hrs.remove("TO")
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

#print(start_hrs)
#print(end_hrs)

#print(len(start_hrs) == len(end_hrs))
final_val = {}
vals = list()
for i in range(len(start_hrs)):
    start_hr = start_hrs[i]
    end_hr = end_hrs[i]
    for day in days:
        final_val[day] = [{"from": start_hr , "to": end_hr}]
    ne_v = {'opening_hours': final_val}
    print(ne_v)


