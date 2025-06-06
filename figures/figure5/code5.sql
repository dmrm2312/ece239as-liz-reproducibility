SELECT 
  autonomous_system.asn AS asn_number,
  COUNT(*) AS count
FROM 
  `ece239as-455719.censys.20250407_superHosts`
WHERE 
  autonomous_system.asn IS NOT NULL
GROUP BY 
  asn_number
ORDER BY 
  count DESC
LIMIT 20;