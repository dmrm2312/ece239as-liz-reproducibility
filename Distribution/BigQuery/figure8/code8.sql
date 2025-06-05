-- Query to analyze super host spin-up patterns by hour and day of week
SELECT 
  EXTRACT(HOUR FROM snapshot_date) AS hour_of_day,
  EXTRACT(DAYOFWEEK FROM snapshot_date) AS day_of_week,
  COUNT(*) AS spinup_count
FROM 
  `ece239as-455719.censys.20250407_superHosts`
WHERE 
  snapshot_date IS NOT NULL
GROUP BY 
  hour_of_day, day_of_week
ORDER BY 
  day_of_week, hour_of_day;

-- Alternative query focusing on timezone distribution without using UNNEST
SELECT 
  location.timezone AS time_zone,
  EXTRACT(DATE FROM snapshot_date) AS spinup_date,
  COUNT(*) AS host_count
FROM 
  `ece239as-455719.censys.20250407_superHosts`
WHERE 
  snapshot_date IS NOT NULL
  AND location.timezone IS NOT NULL
GROUP BY 
  time_zone, spinup_date
ORDER BY 
  spinup_date, host_count DESC;