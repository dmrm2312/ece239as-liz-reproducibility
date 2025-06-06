-- Limit to 50 SuperHosts with computed diversity label
WITH superhosts AS (
  SELECT 
    host_ip,
    COUNT(DISTINCT port) AS open_port_count,
    COUNT(DISTINCT service) AS service_diversity,
    COUNT(DISTINCT service) / NULLIF(COUNT(DISTINCT port), 0) AS service_to_port_ratio
  FROM `censys_scans.ipv4_services`
  WHERE scan_date BETWEEN '2025-04-01' AND '2025-04-07'
  GROUP BY host_ip
  HAVING open_port_count >= 50
),
threshold AS (
  SELECT 
    PERCENTILE_CONT(service_to_port_ratio, 0.8) OVER() AS ratio_threshold
  FROM superhosts
)
SELECT 
  s.host_ip,
  s.open_port_count,
  s.service_diversity,
  s.service_to_port_ratio,
  IF(s.service_to_port_ratio > t.ratio_threshold, 1, 0) AS high_diversity
FROM superhosts s
CROSS JOIN threshold t
LIMIT 50