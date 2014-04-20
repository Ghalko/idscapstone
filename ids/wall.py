from pandas import *
from ggplot import *


def dataplot(df, lab, xl=None, yl=None, title=None):
    """Plot the label given of the dataframe"""
    plot = ggplot(mdata, aes('DATETIME', lab)) +\
        geom_line(color='red') +\
        ggtitle(title) +\
        xlab(xl) +\
        ylab(yl) +\
        scale_x_date(breaks=date_breaks('1 month'), labels='%b')
    print plot

def smooth(df, lab):
    """Smooths spikes in labeled column of dataframe."""
    df_len = len(df.index)
    for i, count in df.iterrows():
        if (i - 2 < 0) or (i+2 > (df_len - 1)):
            continue
        avg_count_low = (df[lab][i-2] + df[lab][i-1])/2
        avg_count_high = (df[lab][i+2] + df[lab][i+1])/2
        if (((avg_count_high - avg_count_low) > 10000) or
            ((avg_count_low - avg_count_high) > 10000)):
            continue #because it may be a step.
        if count[lab] < df[lab][i-1] or count[lab] > df[lab][i+1]:
            df[lab][i] =  int((df[lab][i+1] + df[lab][i-1])/2)
    return df

def detectSteps(df, lab, step):
    """Remove steps from data bove step size in lab column"""
    df_len = len(df.index)
    for i, count in df.iterrows():
        if (i - 1 < 0) or (i+2 > (df_len - 1)):
            continue
        if df[lab][i] < df[lab][i-1]:
            if df[lab][i+2] > df[lab][i-1]: # A two step
                if df[lab][i+2]-df[lab][i-1] > 3*step: #Right before large step
                    print "Run detect steps a second time."
                    print str(df[lab][i+2]-df[lab][i-1]) + " " + str(i)
                    continue
                else:
                    df[lab][i] = df[lab][i-1] + (df[lab][i+2] - df[lab][i-1])/3
                    df[lab][i+1] = df[lab][i-1] + (df[lab][i+2] - df[lab][i-1])*(2/3)
            else:
                df[lab][i:] = df[lab][i:] + (df[lab][i-1]-df[lab][i]) + (df[lab][i-1] - df[lab][i-2]) #gives the previous diff...
        elif (df[lab][i]-df[lab][i-1]) > step:
            take_away = (df[lab][i]-df[lab][i-1])-(df[lab][i-1] - df[lab][i-2])
            df[lab][i:] = df[lab][i:] - take_away
    return df


def usage():
    print """Takes a filename, label as a list
Optional: xl (x-label), yl (y-label), title, maxstep"""


def cycle_file(filename=None, label=None, **kwargs):
    maxstep = 10000
    if filename is None or label is None or not isinstance(label, list):
        usage()
        return
    if 'maxstep' in kwargs:
        maxstep=kwargs['maxstep']
    mdata = pandas.read_csv(filename)
    #setting datetime to a datetime object within pandas
    mdata['DATETIME'] = pandas.to_datetime(mdata['DATETIME'])
    for lab in label:
        mdata = smooth(mdata, lab)
        mdata = detectSteps(mdata, lab, maxstep)
        mdata = detectSteps(mdata, lab, maxstep)
        dataplot(mdata, lab, kwargs)
    return mdata
    
if __name__=="__main__":
    filename = "/export/data/bgorges/udacityIDS/data/wall.csv"
    mdata = cycle_file(filename, ["ENTRIES", "EXITS"])
    mdata.to_csv("/export/data/bgorges/udacityIDS/data/cleanWall.csv")

