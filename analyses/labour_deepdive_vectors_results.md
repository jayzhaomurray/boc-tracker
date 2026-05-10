# Labour Deep-Dive Vector Probe Results
Date: 2026-05-09

## LFS Reason for Unemployment — Table 14-10-0125-01

getCubeMetadata status: SUCCESS

Table title: Reason for leaving job during previous year, monthly, unadjusted for seasonality
Frequency: N/A

### Dimension: Geography
  - [1] Canada
  - [2] Newfoundland and Labrador
  - [3] Prince Edward Island
  - [4] Nova Scotia
  - [5] New Brunswick
  - [6] Quebec
  - [7] Ontario
  - [8] Manitoba
  - [9] Saskatchewan
  - [10] Alberta
  - [11] British Columbia

### Dimension: Reason
  - [1] Total, all reasons
  - [2] Job leavers
  - [3] Own illness or disability
  - [4] Personal or family reasons
  - [5] Going to school
  - [6] Dissatisfied
  - [7] Retired
  - [8] Other reasons
  - [9] Jobs losers
  - [10] Permanent layoff
  - [11] Temporary layoff
  - [12] Have not worked in last year
  - [13] Never worked

### Dimension: Characteristics
  - [1] Total, unemployed and not in the labour force
  - [2] Unemployed
  - [3] Not in the labour force

### Dimension: Gender
  - [1] Total - Gender
  - [2] Men+
  - [3] Women+

### Dimension: Age group
  - [1] 15 years and over
  - [2] 15 to 24 years
  - [3] 25 years and over
  - [4] 25 to 54 years
  - [5] 55 years and over
  - [6] 55 to 64 years
  - [7] 65 years and over

## LFS Reason — Direct Vector Probes (Job Losers)

Vector 2062849: Canada;Part-time employment;Men+;15 to 24 years;Estimate;Seasonally adjusted
Vector 2062850: Canada;Unemployment;Men+;15 to 24 years;Estimate;Seasonally adjusted
Vector 2062851: Canada;Unemployment rate;Men+;15 to 24 years;Estimate;Seasonally adjusted
Vector 2062852: Canada;Participation rate;Men+;15 to 24 years;Estimate;Seasonally adjusted
Vector 80691: ERROR — 'NoneType' object has no attribute 'lower'
Vector 80692: ERROR — 'NoneType' object has no attribute 'lower'
Vector 80693: ERROR — 'NoneType' object has no attribute 'lower'
Vector 2062856: Canada;Employment;Women+;15 to 24 years;Estimate;Seasonally adjusted
Vector 2062857: Canada;Full-time employment;Women+;15 to 24 years;Estimate;Seasonally adjusted
Vector 41704532: Saskatchewan;Breweries
Vector 41704533: Saskatchewan;Tobacco manufacturing

## Youth & Prime-Age Unemployment — Table 14-10-0287-01

getCubeMetadata status: SUCCESS

Table title: Labour force characteristics, monthly, seasonally adjusted and trend-cycle
Frequency: N/A

### Dimension: Geography
  - [1] Canada
  - [2] Newfoundland and Labrador
  - [3] Prince Edward Island
  - [4] Nova Scotia
  - [5] New Brunswick
  - [6] Quebec
  - [7] Ontario
  - [8] Manitoba
  - [9] Saskatchewan
  - [10] Alberta
  - [11] British Columbia

### Dimension: Labour force characteristics
  - [1] Population
  - [2] Labour force
  - [3] Employment
  - [4] Full-time employment
  - [5] Part-time employment
  - [6] Unemployment
  - [7] Unemployment rate
  - [8] Participation rate
  - [9] Employment rate

### Dimension: Gender
  - [1] Total - Gender
  - [2] Men+
  - [3] Women+

### Dimension: Age group
  - [1] 15 years and over
  - [8] 15 to 64 years
  - [2] 15 to 24 years
  - [3] 15 to 19 years
  - [4] 20 to 24 years
  - [5] 25 years and over
  - [6] 25 to 54 years
  - [7] 55 years and over
  - [9] 55 to 64 years

### Dimension: Statistics
  - [1] Estimate
  - [2] Standard error of estimate
  - [3] Standard error of month-to-month change
  - [4] Standard error of year-over-year change

### Dimension: Data type
  - [1] Seasonally adjusted
  - [3] Trend-cycle
  - [2] Unadjusted

## Youth/Prime-Age Unemployment — Direct Vector Probes

Vector 2062825: Canada;Participation rate;Men+;15 years and over;Estimate;Seasonally adjusted
Vector 2062826: Canada;Employment rate;Men+;15 years and over;Estimate;Seasonally adjusted
Vector 2062827: Canada;Population;Women+;15 years and over;Estimate;Seasonally adjusted
Vector 2062828: Canada;Labour force;Women+;15 years and over;Estimate;Seasonally adjusted
Vector 2062829: Canada;Employment;Women+;15 years and over;Estimate;Seasonally adjusted
Vector 2062830: Canada;Full-time employment;Women+;15 years and over;Estimate;Seasonally adjusted
Vector 2062831: Canada;Part-time employment;Women+;15 years and over;Estimate;Seasonally adjusted
Vector 2062832: Canada;Unemployment;Women+;15 years and over;Estimate;Seasonally adjusted
  ** CANDIDATE — Latest: [('2026-03-01', 693.5), ('2026-04-01', 724.3)]
Vector 2062833: Canada;Unemployment rate;Women+;15 years and over;Estimate;Seasonally adjusted
  ** CANDIDATE — Latest: [('2026-03-01', 6.5), ('2026-04-01', 6.8)]
Vector 2062834: Canada;Participation rate;Women+;15 years and over;Estimate;Seasonally adjusted
Vector 2062835: Canada;Employment rate;Women+;15 years and over;Estimate;Seasonally adjusted
Vector 2062836: Canada;Population;Total - Gender;15 to 24 years;Estimate;Seasonally adjusted
  ** CANDIDATE — Latest: [('2026-03-01', 4974.7), ('2026-04-01', 4967.5)]
Vector 2062837: Canada;Labour force;Total - Gender;15 to 24 years;Estimate;Seasonally adjusted
  ** CANDIDATE — Latest: [('2026-03-01', 3120.1), ('2026-04-01', 3123.4)]
Vector 2062838: Canada;Employment;Total - Gender;15 to 24 years;Estimate;Seasonally adjusted
  ** CANDIDATE — Latest: [('2026-03-01', 2688.5), ('2026-04-01', 2677.7)]
Vector 2062839: Canada;Full-time employment;Total - Gender;15 to 24 years;Estimate;Seasonally adjusted
  ** CANDIDATE — Latest: [('2026-03-01', 1318.5), ('2026-04-01', 1289.3)]
Vector 2062840: Canada;Part-time employment;Total - Gender;15 to 24 years;Estimate;Seasonally adjusted
  ** CANDIDATE — Latest: [('2026-03-01', 1370.0), ('2026-04-01', 1388.4)]

## EI Regular Beneficiaries — Table 14-10-0005-01

getCubeMetadata status: SUCCESS

Table title: Employment insurance claims received by province and territory, monthly, seasonally adjusted
Frequency: N/A

### Dimension: Geography
  - [1] Canada
  - [2] Newfoundland and Labrador
  - [3] Prince Edward Island
  - [4] Nova Scotia
  - [5] New Brunswick
  - [6] Quebec
  - [7] Ontario
  - [8] Manitoba
  - [9] Saskatchewan
  - [10] Alberta
  - [11] British Columbia
  - [12] Yukon
  - [13] Northwest Territories including Nunavut
  - [15] Northwest Territories
  - [16] Nunavut
  - [14] Outside Canada

### Dimension: Type of claim
  - [1] Initial and renewal claims
  - [2] Initial claims
  - [3] Renewal claims
  - [4] Initial and renewal claims, seasonally adjusted

### Dimension: Claim detail
  - [1] Received
  - [2] Allowed

## EI — Direct Vector Probes

Vector 1365054: None
Vector 1365054: ERROR — 'NoneType' object has no attribute 'lower'
Vector 1365055: None
Vector 1365055: ERROR — 'NoneType' object has no attribute 'lower'
Vector 1365056: None
Vector 1365056: ERROR — 'NoneType' object has no attribute 'lower'
Vector 1365057: None
Vector 1365057: ERROR — 'NoneType' object has no attribute 'lower'
Vector 1365058: None
Vector 1365058: ERROR — 'NoneType' object has no attribute 'lower'
Vector 1365060: None
Vector 1365060: ERROR — 'NoneType' object has no attribute 'lower'
Vector 1365061: None
Vector 1365061: ERROR — 'NoneType' object has no attribute 'lower'
Vector 1365062: None
Vector 1365062: ERROR — 'NoneType' object has no attribute 'lower'
Vector 1365063: None
Vector 1365063: ERROR — 'NoneType' object has no attribute 'lower'
Vector 41700193: Yukon;Pipeline transportation
Vector 41700194: Yukon;Pipeline transportation
Vector 41700195: Yukon;Pipeline transportation of natural gas

