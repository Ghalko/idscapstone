import pandas
import pandasql

#look at seaborn for pandas visualization.

def sql_query(data=None, query=None, cols=None, index=None):
    """Takes dataframe, query, and columns, index, returns dataframe.
    Query needs to have 'data' as table."""
    if data is None or query is None or cols is None or index is None:
        print "Missing input."
        return
    ndata = pandasql.sqldf(query.lower(), locals())
    ndata.columns = cols
    ndata = ndata.set_index(index)
    return ndata

def sub_data(data=None, col=None, new=None, shift=1):
    if data is None or col is None:
        print "missing data or column"
        return            
    if new is None:
        new = col + "_shifted"
    data[new] = data[col] - data.shift(shift)[col]
    data = data.fillna(1)
    return data

def extract_hour(data=None):
    data['HOUR'] = data.DATETIME.map(lambda x: int(x[11])*10 + int(x[12]))
    return data

if __name__=="__main__":
    master = "/export/data/bgorges/udacityIDS/data/cleanWall.csv"
    #Read csv file
    mta_data = pandas.read_csv(master)
    mta_data = extract_hour(mta_data)
    #shifts by one and subtracts.
    mta_data = sub_data(mta_data, 'ENTRIES', 'ENTRIES_hourly')
    mta_data = sub_data(mta_data, 'EXITS', 'EXITS_hourly')
    print mta_data.describe() #just to see what's coming.
    
    #--- Group by time over all the data ------------------------
    q = '''SELECT hour,avg(cast(entries_hourly as integer)),
avg(cast(exits_hourly as integer)) FROM mta_data
GROUP BY hour'''
    group1 = sql_query(mta_data, q, ['HOUR', 'AVG_ENTRIES', 'AVG_EXITS'],
                       'HOUR')

filename = "/export/data/bgorges/udacityIDS/data/avg_per_hour_all.csv"
group1.to_csv(filename)
print "All done."
#-------------------------------------------------------------

#--- by weekends --------------------------------------------
q = '''SELECT hour,avg(cast(entries_hourly as integer)),
avg(cast(exits_hourly as integer)) FROM mta_data
WHERE cast(strftime('%w', datetime) as integer)=0
OR cast(strftime('%w', datetime) as integer)=6
GROUP BY hour;'''
group2 = pandasql.sqldf(q.lower(), locals())
group2.columns = ['HOUR', 'AVG_ENTRIES', 'AVG_EXITS']
group2 = group2.set_index('HOUR')

filename = "/export/data/bgorges/udacityIDS/data/avg_per_hour_wkends.csv"
group2.to_csv(filename)
print "Weekends done."
#-----------------------------------------------------------

#--- by weekdays -------------------------------------------
q = '''SELECT hour,avg(cast(entries_hourly as integer)),
avg(cast(exits_hourly as integer)) FROM mta_data
WHERE cast(strftime('%w', datetime) as integer)<>0
OR cast(strftime('%w', datetime) as integer)<>6
GROUP BY hour;'''
group3 = pandasql.sqldf(q.lower(), locals())
group3.columns = ['HOUR', 'AVG_ENTRIES', 'AVG_EXITS']
group3 = group3.set_index('HOUR')

filename = "/export/data/bgorges/udacityIDS/data/avg_per_hour_wk.csv"
group3.to_csv(filename)
print "done"
