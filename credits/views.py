from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.db.models.functions import ExtractHour, TruncHour
from records.models import Station, StationLimit, Sensor, Record
import json, requests
from rest_framework import serializers
from django.db.models import Avg, Count, Min, Sum
from decimal import *


base_url = "http://api.foursquare.com/v2/venues/"
CLIENT_ID = "client_id=DKWKZYDJT4ACKUS22JVI5LRW54O2XHZF00SQTTVE3OIEZNBJ"
SECRET_KEY = "client_secret=C143PM0QCCTQ5DJ3ZMWZVPUEQHB3O4WW5LLRXSET5P5EPCSB"
API_V = "v=20200828"



def index(request):
    get_url = f"{base_url}search?ll=43.643201,51.161871&{CLIENT_ID}&{SECRET_KEY}&{API_V}"
    r = requests.get(get_url)
    return HttpResponse(f"Salam world! {get_url} <br/> {r.json()}")

class Venue():

    def __init__(self):
        self._name = name
        self._address = address
def get_last_dates():
    last = Record.get_latest()
    last_date = last.datetime.date()
    start_date = datetime(last_date.year, last_date.month, last_date.day)
    end_date = start_date + timedelta(days=1, microseconds=-1)
    return (start_date, end_date)


def get_last_times():

    last = Record.get_latest()
    last_dt = last.datetime
    last_date = last_dt.strftime("%d.%m.%Y")
    last_time = last_dt.strftime("%d.%m.%Y %H:%M")
    # last_time = str(last_dt.time())[0:5]
    last_hour = last_dt.hour
    last_min = last_dt.minute
    print("last record: ", last)
    print("last datetime: ", last_dt)
    print("last_date: ", last_date)
    print("last hour: ", last_hour)
    print("last minute: ", last_min)

    last_quarter = 0
    if last_min == 0:
        last_quarter = 1
    elif last_min == 15:
        last_quarter = 2
    elif last_min == 30:
        last_quarter = 3
    elif last_min == 45:
        last_quarter = 4
    print('last_quarter: ', last_quarter)
    return (last_dt, last_date, last_time, last_hour, last_min, last_quarter)


class ListSerializer(serializers.ModelSerializer):
    extra_data = serializers.SerializerMethodField()
    class Meta:
        model = Station
        fields = ('name', 'extra_data')

    def get_extra_data(self, station):
        (start_date, end_date) = get_last_dates()

        filter_hour = self.context['hour']
        value_arr = []

        limits = station.get_limits()

        k = 0
        j= 0
        avg = 0
        for i in range(4):
            records = (Record.objects
                       .filter(sensor__station=station, datetime__range=(start_date, end_date))
                       .filter(datetime__hour=filter_hour['hour'], datetime__minute=k))
            k+=15
            sum = records.aggregate(Sum('value')).get('value__sum')
            
            status = 0
            if sum is not None:
                sum = round(((sum * 4) / 1000), 2)
                # sum = round(sum,2)
                avg += sum
                j += 1
            try:
                if limits.max<sum:
                    status = 1
                if limits.min>sum:
                    status = -1
            except:
                pass

            value = {
                "value": sum if sum is not None else "" ,
                "status": status
            }
            # print(value)
            value_arr.append(value)
        avg = round((avg/j), 2)
        avg_status = 0
        if limits.max < avg:
            avg_status = 1
        if limits.min > avg:
            avg_status = -1

        result = {
            'values': value_arr,
            'avg': avg,
            'avg_status': avg_status
        }

        return result

    # def to_representation(self, extra_data):
    #     print("extra_data: ", extra_data)
    #     return 0


class MainSerializer(serializers.Serializer):
    hour = serializers.IntegerField()

    def to_representation(self, hour):

        stations = Station.objects.all().exclude(name="СУММАРНО")
        row = ListSerializer(stations, many=True, context = {"hour": hour}).data
        repr_hour = str(hour['hour']) + ':00'
        res = {
            'hour': repr_hour,
            'data': row
        }
        return res


def indexo(request):
    template_name = 'records/indexvue.html'
    sum_station = "СУММАРНО"

    (last_dt, last_date, last_time, last_hour, last_min, last_quarter) = get_last_times()
    (start_date, end_date) = get_last_dates()

    records = Record.objects.filter(datetime__range=(start_date, end_date)).order_by('datetime')

    stations_limit = [] # NOTE limits by station in dict
    last_records = [] # NOTE last_records is values inside heading for last quarter and hour
    # last_records_agg = {}

    hours = (Record.objects
             .filter(datetime__range=(start_date, end_date))
             .annotate(hour=ExtractHour('datetime'))
             .values_list('hour', flat=True)
             .order_by('datetime')
             .distinct())
    hours = sorted(set(hours), reverse=True)
    hours = [{'hour': item} for item in hours]
    # print('hours: ', hours)

    records_json = json.dumps(MainSerializer(hours, many=True).data, ensure_ascii=False)
    # records_json = MainSerializer(hours, many = True).data


    for station in Station.objects.all():
        stations_limit.append(station.get_limits_dict())

        if station.name != sum_station:
            # NOTE records for last quarter
            last_quarter_records = records.filter(
                sensor__station = station,
                datetime=last_dt)
            # NOTE records for last hour
            last_hour_records = records.filter(
                sensor__station = station,
                datetime__contains=last_dt.strftime("%Y-%m-%d %H"))

            last_quarter_value = 0
            for obj in last_quarter_records:
                # print(f"{obj.id}-{obj.value}")
                last_quarter_value += obj.value

            last_hour_value = 0
            for obj in last_hour_records:
                # print(f"{obj.id}-{obj.value}")
                last_hour_value += obj.value

            print("last_quarter_value: ", last_quarter_value)
            print("last_hour_value: ", last_hour_value)
            limits = station.get_limits()
            my_dict = {
                "station": station.name,
                "value": round(((last_quarter_value * 4) / 1000), 2),
                "sum": round(((last_hour_value * 4) / 1000), 2),
                "min": limits.min,
                "max": limits.max
            }
            last_records.append(my_dict)
            # last_records_agg[station.name] = agg_value
    sum_limits = StationLimit.objects.filter(station__name=sum_station).order_by('updateTime').last()
    sum_dict = {
        "station": sum_station,
        "value": sum(item['value'] for item in last_records),
        "sum": sum(item['sum'] for item in last_records),
        "min": sum_limits.min,
        "max": sum_limits.max
    }
    last_records.append(sum_dict)
    # print("last_records: ", json.dumps(last_records, ensure_ascii=False))

    # records_serial = RecordSerializer(last_quarter_records, many=True).data
    # last_records_agg[sum_station] = sum(last_records_agg.values())

    context = {
        'last_date': json.dumps(last_date, ensure_ascii=False),
        'last_time': json.dumps(last_time, ensure_ascii=False),
        'last_hour': last_hour,
        'last_min': last_min,
        'last_quarter': last_quarter,
        'stations_limit': json.dumps(stations_limit, ensure_ascii=False),
        'last_records': json.dumps(last_records, ensure_ascii=False),
        # 'records': json.dumps(records_serial),
        'records': records_json,
    }
    # print('context: ', context)
    print(records_json)
    return render(request, template_name, context)


def dump_json():
    my_js = [
        {
            "hour": "13:00",
            "data": [
                {
                    "station": "ТЭЦ-1",
                    "values": [
                        {"value": "30", "status": "1"},
                        {"value": "35", "status": "1"},
                        {"value": "", "status": ""},
                        {"value": "", "status": ""}
                    ],
                    "avg": "65",
                    "avg_status": "1"
                },
                {
                    "station": "ТЭЦ-2",
                    "values": [
                        {"value": "300", "status": "1"},
                        {"value": "320", "status": "1"},
                        {"value": "", "status": ""},
                        {"value": "", "status": ""},
                    ],
                    "avg": "620",
                    "avg_status": "1"
                },
                {
                    "station": "ТЭС",
                    "values": [
                        {"value": "120", "status": "1"},
                        {"value": "150", "status": "1"},
                        {"value": "", "status": "1"},
                        {"value": "", "status": "1"},
                    ],
                    "avg": "270",
                    "avg_status": "-1"
                },
                {
                    "station": "СУММАРНО",
                    "values": [
                        {"value": "600", "status": "0"},
                        {"value": "300", "status": "1"},
                        {"value": "", "status": "1"},
                        {"value": "", "status": "1"},
                    ],
                    "avg": "900",
                    "avg_status": "0"
                }
            ]
        },
        {
            "hour": "12:00",
            "data": [
                {
                    "station": "ТЭЦ-1",
                    "values": [
                        {"value": "40", "status": "-1"},
                        {"value": "20", "status": "0"},
                        {"value": "", "status": ""},
                        {"value": "", "status": ""},
                    ],
                    "avg": "60",
                    "avg_status": "0"
                },
                {
                    "station": "ТЭЦ-2",
                    "values": [
                        {"value": "310", "status": "0"},
                        {"value": "320", "status": "0"},
                        {"value": "", "status": ""},
                        {"value": "", "status": ""},
                    ],
                    "avg": "630",
                    "avg_status": "1"
                },
                {
                    "station": "ТЭС",
                    "values": [
                        {"value": "130", "status": "-1"},
                        {"value": "100", "status": "-1"},
                        {"value": "", "status": ""},
                        {"value": "", "status": ""},
                    ],
                    "avg": "230",
                    "avg_status": "0"
                },
                {
                    "station": "СУММАРНО",
                    "values": [
                        {"value": "500", "status": "-1"},
                        {"value": "450", "status": "-1"},
                        {"value": "", "status": ""},
                        {"value": "", "status": ""},
                    ],
                    "avg": "950",
                    "avg_status": "-1"
                }
            ]
        },
        {
            "hour": "11:00",
            "data": [
                {
                    "station": "ТЭЦ-1",
                    "values": [
                        {"value": "30", "status": "1"},
                        {"value": "35", "status": "1"},
                        {"value": "", "status": ""},
                        {"value": "", "status": ""}
                    ],
                    "avg": "65",
                    "avg_status": "1"
                },
                {
                    "station": "ТЭЦ-2",
                    "values": [
                        {"value": "300", "status": "1"},
                        {"value": "320", "status": "1"},
                        {"value": "", "status": ""},
                        {"value": "", "status": ""},
                    ],
                    "avg": "620",
                    "avg_status": "1"
                },
                {
                    "station": "ТЭС",
                    "values": [
                        {"value": "120", "status": "1"},
                        {"value": "150", "status": "1"},
                        {"value": "", "status": "1"},
                        {"value": "", "status": "1"},
                    ],
                    "avg": "270",
                    "avg_status": "-1"
                },
                {
                    "station": "СУММАРНО",
                    "values": [
                        {"value": "600", "status": "0"},
                        {"value": "300", "status": "1"},
                        {"value": "", "status": "1"},
                        {"value": "", "status": "1"},
                    ],
                    "avg": "900",
                    "avg_status": "0"
                }
            ]
        },
    ]
    return my_js