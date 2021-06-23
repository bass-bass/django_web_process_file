import pandas as pd
import numpy as np
import sklearn,csv,re,os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from django.http import HttpResponse
from myproject.settings import BASE_DIR

def process_file(df):
    #train_x = pd.read_csv("app/static/files/train_x_modified.csv")
    #train_y = pd.read_csv("app/static/files/train_y_modified.csv")
    train_x = pd.read_csv(os.path.join(BASE_DIR, 'app/static/files/train_x_modified.csv'))
    train_y = pd.read_csv(os.path.join(BASE_DIR, 'app/static/files/train_y_modified.csv'))
    test_x = df
    df1 = test_x["お仕事No."]
    
    test_x = test_x.reindex(columns=train_x.columns)
    A = ["（派遣先）配属先部署　男女比　男","（派遣先）配属先部署　人数","勤務地　最寄駅1（分）","（派遣先）配属先部署　男女比　女","（派遣先）配属先部署　平均年齢"]
    for item in A:
        test_x[item] = test_x[item].fillna(train_x[item].median())

    test_x["勤務地　最寄駅1（駅からの交通手段）"] = test_x["勤務地　最寄駅1（駅からの交通手段）"].fillna(0)

    df_test = test_x["給与/交通費　備考"]
    df_test = df_test.astype(object)

    t = pd.DataFrame(df_test)
    for i,row in enumerate(t.iterrows()):
        if type(row[1][0]) == str:
            numbers = re.findall(r"\d+", row[1][0])
            if len(numbers)==2:
                t.iloc[i,0] = int(numbers[0]+"0000")
            elif len(numbers)>=3:
                if len(numbers[1])==2:
                    t.iloc[i,0] = int(numbers[0]+"00"+numbers[1])
                elif len(numbers[1])==3:
                    t.iloc[i,0] = int(numbers[0]+"0"+numbers[1])
                elif len(numbers[1])==4:
                    t.iloc[i,0] = int(numbers[0]+numbers[1])
            elif len(numbers)==0:
                t.iloc[i,0] = 0

    t = t.fillna(t.median())
    test_x["給与/交通費　備考"] = t
    for row in pd.DataFrame(test_x.dtypes).iterrows():
        if row[1][0] == object:
            X = []
            df_2 = pd.DataFrame(test_x[row[0]])
            for k,x in enumerate(df_2.itertuples()):
                if x[1] not in X:
                    X.append(x[1])
                    df_2.iloc[k,0] = X.index(x[1])
                elif x[1] in X:
                    df_2.iloc[k,0] = X.index(x[1])
            test_x[row[0]] = df_2

    x_array = np.array(train_x)
    y_array = np.array(train_y)

    X_train, X_test, y_train, y_test = train_test_split(x_array, y_array, test_size=0.2, random_state=0)
    rfr = RandomForestRegressor(random_state=0)
    rfr.fit(X_train, y_train)

    y_pred = rfr.predict(test_x)
    df2 = pd.DataFrame(y_pred)
    df2 = df2.rename(columns={0: "応募数 合計"})
    df_result = pd.concat([df1,df2],axis=1)

    return df_result



def to_csv(data):

    response = HttpResponse(content_type='text/csv; charset=UTF-8')
    response['Content-Disposition'] = 'attachment; filename="result.csv"'
    
    data.to_csv(path_or_buf = response, encoding = 'utf-8-sig', index=False)
    
    return response