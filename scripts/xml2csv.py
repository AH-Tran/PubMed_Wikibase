# Importing the required libraries
import xml.etree.ElementTree as Xet
import pandas as pd
  
cols = ["name", "phone", "email", "date", "country"]
rows = []
  
# Parsing the XML file
xmlparse = Xet.parse('sample.xml')
root = xmlparse.getroot()
for i in root:
    name = i.find("name").text
    phone = i.find("phone").text
    email = i.find("email").text
    date = i.find("date").text
    country = i.find("country").text
  
    rows.append({"name": name,
                 "phone": phone,
                 "email": email,
                 "date": date,
                 "country": country})
  
df = pd.DataFrame(rows, columns=cols)
  
# Writing dataframe to csv
df.to_csv('output.csv')