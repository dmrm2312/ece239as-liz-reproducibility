-- Simplified query for country-level aggregation (bar chart)
SELECT 
  location.country AS country,
  COUNT(*) AS host_count
FROM 
  `ece239as-455719.censys.20250407_superHosts`
WHERE 
  location.country IS NOT NULL
GROUP BY 
  country
ORDER BY 
  host_count DESC
LIMIT 32;