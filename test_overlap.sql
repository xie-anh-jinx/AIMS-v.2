SELECT count(*) AS safe_count FROM academic_records WHERE status != 'HIGH_RISK' AND status != 'Warning' AND (status = 'Aman' OR ipk >= 2.75);
SELECT count(*) AS warn_count FROM academic_records WHERE status != 'HIGH_RISK' AND (status = 'Warning' OR (ipk >= 2.0 AND ipk < 2.75));
SELECT count(*) AS overlap_count FROM academic_records WHERE (status != 'HIGH_RISK' AND status != 'Warning' AND (status = 'Aman' OR ipk >= 2.75)) AND (status != 'HIGH_RISK' AND (status = 'Warning' OR (ipk >= 2.0 AND ipk < 2.75)));
