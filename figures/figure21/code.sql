SELECT 
  host_ip,
  port,
  service,
  CONCAT(service, '-', CAST(port AS STRING)) AS service_port_pair,
  CASE 
    WHEN REGEXP_CONTAINS(organization_name, r'(?i)(aws|amazon|azure|microsoft|google|cloud)') THEN 'Cloud'
    ELSE 'Non-Cloud' 
  END AS asn_type
FROM `censys_scans.ipv4_services`
WHERE scan_date BETWEEN '2025-04-01' AND '2025-04-07'
  AND host_ip IN (
    SELECT host_ip 
    FROM `censys_scans.ipv4_services`
    WHERE scan_date BETWEEN '2025-04-01' AND '2025-04-07`
    GROUP BY host_ip
    HAVING COUNT(DISTINCT port) >= 50
  )
ORDER BY host_ip, port
LIMIT 30