SELECT 
  host_ip,
  COUNT(DISTINCT port) AS open_port_count,
  COUNT(DISTINCT service) AS service_diversity,
  COUNTIF(service = 'UNKNOWN') AS unknown_service_count,
  COUNT(DISTINCT service) / NULLIF(COUNT(DISTINCT port), 0) AS service_to_port_ratio,
  os_name,
  organization_name,
  CASE
    WHEN COUNT(DISTINCT port) >= 35 AND COUNT(DISTINCT service) <= 2 THEN 'Containerized'
    WHEN COUNT(DISTINCT port) BETWEEN 15 AND 25 AND COUNT(DISTINCT service) >= 8 THEN 'Non-Containerized'
    ELSE 'Other'
  END AS deployment_type
FROM `censys_scans.ipv4_services`
WHERE scan_date BETWEEN '2025-04-01' AND '2025-04-07'
GROUP BY host_ip, os_name, organization_name
HAVING deployment_type IN ('Containerized', 'Non-Containerized')
LIMIT 40