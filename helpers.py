from datetime import datetime

def get_age(birthmonth, birthday, birthyear):
    currentyear = datetime.now().year
    currentmonth = datetime.now().month
    currentday = datetime.now().day
    if currentyear >= birthyear:
        if currentmonth < birthmonth:
            age = (currentyear - birthyear) - 1
        elif currentmonth > birthmonth:
            age = currentyear - birthyear
        elif currentmonth == birthmonth:
            if currentday >= birthday:
                age = currentyear - birthyear
            else:
                age = (currentyear - birthyear) - 1
    return age