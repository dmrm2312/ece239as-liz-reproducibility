SELECT 
  host_ip,
  COUNT(DISTINCT service) AS service_diversity,
  COUNT(DISTINCT service) / NULLIF(COUNT(DISTINCT port), 0) AS service_to_port_ratio,
  organization_name
FROM `censys_scans.ipv4_services`
WHERE scan_date BETWEEN '2025-04-01' AND '2025-04-07'
  AND port IN UNNEST([21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 161, 389, 443, 445, 465, 514, 993, 995, 1025, 
                      1080, 1194, 1433, 1521, 1723, 1900, 2049, 3306, 3389, 5060, 5432, 5900, 5985, 5986, 8000, 8080, 
                      8443, 8888, 9200, 10000]) -- 40 common ports
  AND host_ip IN (
    SELECT host_ip 
    FROM `censys_scans.ipv4_services`
    WHERE scan_date BETWEEN '2025-04-01' AND '2025-04-07'
      AND port IN UNNEST([21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 161, 389, 443, 445, 465, 514, 993, 995, 1025, 
                          1080, 1194, 1433, 1521, 1723, 1900, 2049, 3306, 3389, 5060, 5432, 5900, 5985, 5986, 8000, 8080, 
                          8443, 8888, 9200, 10000])
    GROUP BY host_ip
    HAVING COUNT(DISTINCT port) >= 20 -- Adjusted threshold for 40-port scans
  )
GROUP BY host_ip, organization_name
ORDER BY service_diversity DESC