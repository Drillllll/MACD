import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math


def calculateEMA(A):
    """
         takes set of data A and calculates EMA for n=len(A) periods
    """
    n = len(A)
    #for a in range(n):
        #print (A.iloc[a])

    alpha = 2 / (n+1)
    numerator = 0
    for i in range(n):
        numerator += (1-alpha)**i * A.iloc[i]

    denominator = 0
    for j in range(n):
        denominator += (1-alpha)**j

    #print(numerator/denominator)
    return (numerator/denominator)



def modifyHeaders(df):
    """
        changes the headers of columns of data frame
        deletes unnecessary columns, adds blank columns for future operations
    """
    renamedColumns = ('Date', 'Opening', 'Closing', 'Max', 'Min', 'Turnover (mln zl)', 'Change')
    df.columns = renamedColumns  # change names of columns
    df = df.drop(columns=['Opening', 'Closing', 'Turnover (mln zl)', 'Change'])  # delete not important columns

    df['value'] = ''  # add new column
    df['EMA26'] = ''
    df['EMA12'] = ''
    df['MACD'] = ''
    df['SIGNAL'] = ''

    return df


def prepareIntersections(df):
    """
        extends data frame by one colum indicating intersection between MACD and SIGNAL. If MACD intersects
        SIGNAL from top the value -1 is written into that row (sell! - red). If MACD inter. SIGNAL from below
        the value 1 is -||- (buy! - green)
    """
    # new column shows the difference between values
    df['difference'] = np.where(df['MACD'] - df['SIGNAL'] > 0, 1, 0)

    # new column shows where the difference column changes values
    # for every row it calculates the difference between value and the previous value
    df['intersection'] = df['difference'].diff()

    # MACD SIGNAL difference intersection
    #  10     5      1          -
    #  8      7      1          0
    #  7      11     0          -1 #sell!

    return df


def visualize(df, fileName):
    """
        show data frame on graph
    """

    plt.plot(df['Date'], df['MACD'], label='MACD')
    plt.plot(df['Date'], df['SIGNAL'], label='SIGNAL')
    plt.plot(df['Date'], df['value'], label='value')




    plt.xlabel('Date')
    plt.ylabel('Value')
    # slice 4 last chars in filename .(csv)
    plt.title(fileName[:-4] + ': MACD, SIGNAL and action value in time')

    plt.legend()

    df = prepareIntersections(df)
    # iterates over the dates where df['intersection'] == 1
    for date in df[df['intersection'] == 1]['Date']:
        plt.axvline(x=date, color='g', linewidth=0.2)

    for date in df[df['intersection'] == -1]['Date']:
        plt.axvline(x=date, color='r', linewidth=0.2)

    n = 5  # Limit the number of x-axis ticks to 5
    x_ticks = plt.xticks()[0]
    plt.xticks(x_ticks[::int(len(x_ticks) / n)])
    # slice in python: sequence[start:stop:step]
    # ^ update xticks by slicing it using step calculated by len(x_ticks) / n




    plt.show()


def simulate(df, fileName):
    """
        simulates the MACD indicator in practice
    """
    actions = 1000
    wallet = 0
    startActionsValue = df['value'][0] * actions

    print(fileName[:-4])  # slice 4 last chars from filename (.csv)
    print('starting actions value: ' + str(startActionsValue))

    # The iterrows() method of a pandas dataframe returns an iterator
    # that yields pairs of (index, row) for each row in the dataframe
    iterators = df.iterrows()
    for index, row in iterators:
        if row['intersection'] == 1:
            howMuchCanIBuy = math.floor(wallet/row['value'])
            wallet -= (row['value'] * howMuchCanIBuy)
            actions += howMuchCanIBuy
        elif row['intersection'] == -1:
            howMuchCanISell = actions
            wallet += row['value'] * howMuchCanISell
            actions -= howMuchCanISell

    wallet = round(wallet, 2)
    leftActionsValue = actions * df['value'].iloc[-1]
    leftActionsValue = round(leftActionsValue, 2)
    print("ending wallet: " + str(wallet) +
          " actions left values: " + str(leftActionsValue))
    print("total: " + str(wallet + leftActionsValue))
    income = wallet + leftActionsValue - startActionsValue
    income = round(income, 2)
    print("Income: " + str(income))
    print()


def prepareDf(df):
    """
        prepare data frame for next operations
    """

    df = df.iloc[::-1]

    df = modifyHeaders(df)
    df['value'] = (df['Max'] + df['Min']) / 2  # calculating avg of max and min value for every date in data frame
    df['EMA12'] = df['value'].rolling(window=13).apply(calculateEMA)  # we pass (n+1) values
    df['EMA26'] = df['value'].rolling(window=27).apply(calculateEMA)  # we pass (n+1) values
    df['MACD'] = df['EMA12'] - df['EMA26']

    df['SIGNAL'] = df['MACD'].rolling(window=10).apply(calculateEMA)  # we pass (n+1) values

    return df


def handleCSV(fileName):

    df0 = pd.read_csv(fileName, header=0)  # create new data frame from csv file
    n = 3  # chosing the time frame: n-days
    df = df0.iloc[::n, :]  # slice the data frame: sequence[start:stop:step]
    df = df.drop(df.index[1000:])  # slice up to 1000th row



    df = prepareDf(df)
    visualize(df, fileName)
    simulate(df, fileName)


def main():
    handleCSV('BNP.csv')
    handleCSV('Amica.csv')
    handleCSV('CCC.csv')




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
