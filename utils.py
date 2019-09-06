from html.parser import HTMLParser

# Function that takes age as integer and returns string of range of ages
def makeAgeBin(age):
    if (age < 18):
        return "< 18 years"
    elif (age >= 18 and age <= 29):
        return "18 to 29 years"
    elif (age >= 30 and age <= 49):
        return "30 to 49 years"
    elif (age >= 50 and age <= 69):
        return "50 to 69 years"
    elif (age >= 70):
        return "> 70 years"

# Function to get one key value pair in list of dicts
def getKeyList(list, keyName):
    newList = []
    for dict in list:
        if keyName in dict:
            newList.append(dict[keyName])
        else:
            continue
    return newList

# Function to compare lists and return unique values
def Diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif

# Function to strip out html tags
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

# Function to strip out html tags
def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data().strip().replace(u'\xa0', u' ')

# Function to check if value can be converted to a float
def is_float(input):
  try:
    num = float(input)
  except ValueError:
    return False
  return True

# Function to check if value can be converted to a int
def is_int(input):
  try:
    num = int(input)
  except ValueError:
    return False
  return True
