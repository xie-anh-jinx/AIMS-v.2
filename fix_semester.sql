UPDATE students SET semester = GREATEST(1, LEAST(14, (2026 - angkatan) * 2));
UPDATE academic_records
SET semester = (
    SELECT semester 
    FROM students 
    WHERE students.id = academic_records.student_id
);
