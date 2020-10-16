import pandas  # add pandas and xlrd into interpreter

data = pandas.read_excel('data.xlsx')  # receiving data from given excel file
print(data)

for i in range(1,377):
    if data['Line'][i] != data['Line'][i-1]:
        print(i+1)

for i in range(1,376):
    if data['To Station'][i] != data['From Station'][i+1]:
        print(i+2)
        print(data['To Station'][i])
