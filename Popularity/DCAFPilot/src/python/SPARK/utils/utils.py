import datetime

def construct_date(date):
    year = int(date[:4])
    month = int(date[4:6])
    day = int(date[6:8])
    return datetime.date(year, month, day)

def getStartDate(train_end):
    date = construct_date(train_end) + datetime.timedelta(days=1)
    return date.strftime('%Y%m%d')

def add_days(start_date,  ndays):
    next_date = start_date + datetime.timedelta(days=ndays)
    return start_date, next_date

def getTrainDataFileNames(train_start, train_end, ndays, trainData):
    begin_date = construct_date(str(train_start))
    end_date = construct_date(str(train_end))
    ndays = ndays - 1
    file_names = []

    if (begin_date > end_date):
        print("Start date (" + str(begin_date) + ") is earlier than end date (" + str(end_date) + ")")
    else:
        while (add_days(begin_date, ndays-1)[1] <  end_date):
            beginDate, nextDate = add_days(begin_date, ndays)
            file_names.append("dataframe-"+beginDate.strftime('%Y%m%d')+"-"+nextDate.strftime('%Y%m%d')+".csv.gz")
            begin_date = nextDate +  datetime.timedelta(days=1)

    if (trainData):
        files = ','.join(file_names)
        return files
    else:
        return file_names
