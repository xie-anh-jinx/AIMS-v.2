UPDATE academic_records SET status = 'Warning' WHERE ipk >= 2.0 AND ipk < 2.75;
UPDATE academic_records SET status = 'HIGH_RISK' WHERE ipk < 2.0;
UPDATE academic_records SET status = 'Aman' WHERE ipk >= 2.75;
