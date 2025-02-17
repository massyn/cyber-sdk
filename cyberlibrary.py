import requests
import os
import datetime
import pandas as pd
import tabulate

class CyberLibrary():
    def __init__(self,**KW):
        self.endpoint = os.environ.get('CYBER_DASHBOARD_ENDPOINT',KW.get('endpoint','http://localhost:8080/api'))
        self.token    = os.environ.get('CYBER_DASHBOARD_TOKEN',KW.get('token','6002920168C3253430A653E16AD36EE88F6E3C7D917A5F245F735D96ABDA67FE'))
        self.dimensions = KW.get('dimensions',['business_unit','team','location'])

        self.meta = {}
        self.data = []

        print(f"Endpoint = {self.endpoint}")

    '''initialise the metric with the key variables it requires'''
    def metric(self,**KW):
        # == metric_id must be set
        if not 'metric_id' in KW:
            raise ValueError("You must specify a metric_id when initialising a metric")
        self.meta['metric_id'] = KW['metric_id']
        
        if not 'title' in KW:
            print("WARNING - title was not set.  Will default to the metric_id")
        self.meta['title'] = KW.get('title',KW['metric_id'])

        if not 'category' in KW:
            print("WARNING - category was not set.  Will default to undefined")
        self.meta['category'] = KW.get('category','undefined')

        if not 'indicator' in KW:
            print("WARNING - indicator was not set.  Will default to false")
        self.meta['indicator'] = KW.get('indicator',False)

        self.meta['slo'] = KW.get('slo',0.95)
        if not 'slo' in KW:
            print("WARNING - slo was not set.  Will default to 0.95")
        else:
            self.meta['slo'] = 0.95
        
        self.meta['slo_min'] = KW.get('slo_min',0.90)
        if not 'slo_min' in KW:
            print("WARNING - slo_min was not set.  Will default to 0.90")
        else:
            self.meta['slo_min'] = 0.90

        self.meta['weight'] = KW.get('weight',0.5)
        if not 'weight' in KW:
            print("WARNING - weight was not set.  Will default to 0.5")
        else:
            if self.meta['weight'] > 1 or self.meta['weight'] < 0:
                print(f"WARNING: weight can only be between 0 and 1.  It was set to {self.meta['weight']}.  Defaulting to 0.5")
                self.meta['weight'] = 0.5

    '''Add a new data point'''
    def add(self,**KW):
        if not 'metric_id' in self.meta:
            raise ValueError("You must initialise the metric first before adding data to it")
        if not 'resource' in KW:
            raise ValueError("You must specify a resource when adding a data point")
        if not 'compliance' in KW:
            print("WARNING: compliance is not specified.  Will be assumed to be 0")
        else:
            if KW['compliance'] > 1 or KW['compliance'] < 0:
                print(f"WARNING: compliance for {KW['resource']} can only be between 0 and 1.  It was set to {KW['compliance']}.  Defaulting to 0")
                KW['compliance'] = 0

        # -- see if the dimensions have been set
        dimensions = {}
        for d in self.dimensions:
            dimensions[d] = KW.get(d,'undefined')

        self.data.append({
            'datestamp'     : KW.get('datestamp',datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')),
            # add the meta data
            'metric_id'     : self.meta['metric_id'],
            'title'         : self.meta['title'],
            'category'      : self.meta['category'],
            'slo'           : self.meta['slo'],
            'slo_min'       : self.meta['slo_min'],
            'weight'        : self.meta['weight'],
            'indicator'     : self.meta['indicator'],

            # add the specific data point details
            'resource'      : KW['resource'],
            'compliance'    : KW.get('compliance',0),
            'detail'        : KW.get('detail',''),
            
            # add the dimensions
        } | dimensions)

    def summary(self):
        df = pd.DataFrame(self.data)
        score = df.groupby(['datestamp','metric_id']).agg(totalok=('compliance', 'sum'), total=('compliance', 'count')).reset_index()
        score['score'] = (score['totalok'] / score['total']) * 100
        score['score'] = score['score'].map(lambda x: f"{x:.2f}%")
        print(tabulate.tabulate(score.to_dict(orient='records'),headers="keys"))

    def publish(self):
        df = pd.DataFrame(self.data)
        csv_data = df.to_csv(index=False)

        print(f"Uploading {len(df)} records to the dashboard...")
        try:
            response = requests.post(self.endpoint, headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "text/csv"
            }, data=csv_data)

            if response.status_code == 200:
                print("SUCCESS - Data successfully uploaded to the dashboard.")
            else:
                print(f"ERROR : Error uploading data to the dashboard: {response.status_code}",True)
                print(response.text)
        except Exception as e:
            print(f"ERROR - Error uploading data to the dashboard: {e}",True)
