WITH service_counts AS (
  SELECT 
    service_name,
    COUNT(*) AS host_count
  FROM 
    `ece239as-455719.censys.20250407_superHosts`,
    UNNEST(service_names_list) AS service_name
  WHERE 
    service_name IS NOT NULL
    AND service_name != ''
    AND service_name NOT LIKE '%filtered%'
    -- ... (rest of filters)
  GROUP BY service_name
)
SELECT 
  service_name,
  host_count,
  ROUND((host_count * 100.0) / (SELECT COUNT(*) FROM `ece239as-455719.censys.20250407_superHosts`), 2) AS percentage_of_superhosts
FROM service_counts
WHERE host_count >= 5
ORDER BY host_count DESC