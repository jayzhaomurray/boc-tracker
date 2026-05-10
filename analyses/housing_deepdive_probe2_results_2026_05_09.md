# Housing Deep-Dive Probe 2 -- 2026-05-09

## 1. Valet data samples for mortgage/CREA candidates

  V80691335 (mortgage rate candidate (val ~6.09)): 175 total obs since 2023
    2026-04-08: 6.09
    2026-04-15: 6.09
    2026-04-22: 6.09
    2026-04-29: 6.09
    2026-05-06: 6.09

  V122514 (unknown (val ~2.24)): 40 total obs since 2023
    2025-12-01: 2.2711
    2026-01-01: 2.2491
    2026-02-01: 2.2492
    2026-03-01: 2.2649
    2026-04-01: 2.2351

  BROKER_AVERAGE_5YR_VRM (broker avg 5yr variable rate): 175 total obs since 2023
    2026-04-09: 3.62
    2026-04-16: 3.62
    2026-04-23: 3.62
    2026-04-30: 3.63
    2026-05-07: 3.67

  FVI_CREA_HOUSE_RESALE_INDEXED_CANADA (CREA resales (indexed)): 38 total obs since 2023
    2025-10-01: 96.68
    2025-11-01: 95.41
    2025-12-01: 92.18
    2026-01-01: 86.74
    2026-02-01: 85.60

  FVI_CREA_HOUSE_SALES_TO_NEW_LISTINGS_CANADA (CREA SNLR): 38 total obs since 2023
    2025-10-01: 51.37
    2025-11-01: 51.76
    2025-12-01: 51.81
    2026-01-01: 46.37
    2026-02-01: 47.63

## 2. V80691335 series metadata from Valet

{
  "terms": {
    "url": "https://www.bankofcanada.ca/terms/"
  },
  "seriesDetails": {
    "name": "V80691335",
    "label": "5-year",
    "description": "Conventional mortgage"
  }
}

## 2b. V122514 series metadata from Valet

{
  "terms": {
    "url": "https://www.bankofcanada.ca/terms/"
  },
  "seriesDetails": {
    "name": "V122514",
    "label": "Overnight rate",
    "description": "Overnight rate"
  }
}

## 3. StatsCan getCubeMetadata -- product ID 34100158

  getCubeMetadata(34100158): HTTP 404
  getCubeMetadata(3410015801): HTTP 404
  getCubeMetadata(341001580): HTTP 404
  getCubeMetadata(34100158001): HTTP 404

## 4. POST probe: candidate under-construction and CMA starts vectors

Using getDataFromVectorsAndLatestNPeriods (POST) to fetch 3 data points each.

First checking BoC Valet for housing-under-construction series...
  Housing/construction keys (24 found):
    FVI_HOUSE_RESALES_12M_CALGARY: Calgary
    FVI_HOUSE_RESALES_12M_CANADA: All of Canada
    FVI_HOUSE_RESALES_12M_EDMONTON: Edmonton
    FVI_HOUSE_RESALES_12M_HALIFAX: Halifax
    FVI_HOUSE_RESALES_12M_HAMILTON: Hamilton
    FVI_HOUSE_RESALES_12M_MONTREAL: Montréal
    FVI_HOUSE_RESALES_12M_OTTAWAGATINEAU: Ottawa-Gatineau
    FVI_HOUSE_RESALES_12M_QUEBEC: Québec
    FVI_HOUSE_RESALES_12M_TORONTO: Toronto
    FVI_HOUSE_RESALES_12M_VANCOUVER: Vancouver
    FVI_HOUSE_RESALES_12M_VICTORIA: Victoria
    FVI_HOUSE_RESALES_12M_WINNIPEG: Winnipeg
    FVI_HOUSE_RESALES_6M_CALGARY: Calgary
    FVI_HOUSE_RESALES_6M_CANADA: All of Canada
    FVI_HOUSE_RESALES_6M_EDMONTON: Edmonton
    FVI_HOUSE_RESALES_6M_HALIFAX: Halifax
    FVI_HOUSE_RESALES_6M_HAMILTON: Hamilton
    FVI_HOUSE_RESALES_6M_MONTREAL: Montréal
    FVI_HOUSE_RESALES_6M_OTTAWAGATINEAU: Ottawa-Gatineau
    FVI_HOUSE_RESALES_6M_QUEBEC: Québec
    FVI_HOUSE_RESALES_6M_TORONTO: Toronto
    FVI_HOUSE_RESALES_6M_VANCOUVER: Vancouver
    FVI_HOUSE_RESALES_6M_VICTORIA: Victoria
    FVI_HOUSE_RESALES_6M_WINNIPEG: Winnipeg

Trying sequential vectors near v52300157 via POST...
  v52300157:  latest=2026-03-01 val=235.852
  v52300158:  latest=2026-03-01 val=15.456
  v52300159:  latest=2026-03-01 val=1.112
  v52300160:  latest=2026-03-01 val=1.78
  v52300161:  latest=2026-03-01 val=5.181
  v52300162:  latest=2026-03-01 val=7.383
  v52300163:  latest=2026-03-01 val=83.83
  v52300164:  latest=2026-03-01 val=53.115
  v52300165:  latest=2026-03-01 val=52.949
  v52300166:  latest=2026-03-01 val=8.996
  v52300167:  latest=2026-03-01 val=3.148
  v52300168:  latest=2026-03-01 val=40.805
  v52300169:  latest=2026-03-01 val=30.502
  v52300170:  latest=2026-01-01 val=246.149
  v52300171:  latest=2026-01-01 val=46.821
  v52300172:  latest=2026-01-01 val=199.328
  v52300173:  latest=2026-01-01 val=17.724
  v52300174:  latest=2026-01-01 val=1.552
  v52300175:  latest=2026-01-01 val=2.067
  v52300176:  latest=2026-01-01 val=6.336
  v52300177:  latest=2026-01-01 val=7.769
  v52300178:  latest=2026-01-01 val=59.899
  v52300179:  latest=2026-01-01 val=62.277
  v52300180:  latest=2026-01-01 val=60.449
  v52300181:  latest=2026-01-01 val=8.909
  v52300182:  latest=2026-01-01 val=4.75
  v52300183:  latest=2026-01-01 val=46.79
  v52300184:  latest=2026-01-01 val=45.8
  v52300185:  latest=2026-03-01 val=248.378
  v52300186:  latest=2026-03-01 val=18.964
  v52300187:  latest=2026-03-01 val=1.69
  v52300188:  latest=2026-03-01 val=1.533
  v52300189:  latest=2026-03-01 val=7.944
  v52300190:  latest=2026-03-01 val=7.798
  v52300191:  latest=2026-03-01 val=61.278
  v52300192:  latest=2026-03-01 val=64.874
  v52300193:  latest=2026-03-01 val=60.824
  v52300194:  latest=2026-03-01 val=8.1
  v52300195:  latest=2026-03-01 val=4.995
  v52300196:  latest=2026-03-01 val=47.729
  v52300197:  latest=2026-03-01 val=42.439
  v52300198:  latest=2026-03-01 val=11.846
  v52300199:  latest=2026-03-01 val=3.457

## 5. getSeriesInfoFromVector via POST

POST getSeriesInfoFromVector: HTTP 406
