-- Clean strict duplicates (same student_id, same course_id)
DELETE FROM grades
WHERE id IN (
    SELECT id
    FROM (
        SELECT id,
               ROW_NUMBER() OVER( PARTITION BY student_id, course_id ORDER BY id DESC ) as row_num
        FROM grades
    ) t
    WHERE t.row_num > 1
);

-- Clean semantic duplicates (same student_id, same course name even if course_id differs)
DELETE FROM grades
WHERE id IN (
    SELECT g.id
    FROM grades g
    WHERE g.id IN (
        SELECT id
        FROM (
            SELECT g2.id, 
                   ROW_NUMBER() OVER( PARTITION BY g2.student_id, c2.nama ORDER BY g2.bobot DESC, g2.id DESC ) as row_num
            FROM grades g2
            JOIN courses c2 ON g2.course_id = c2.id
        ) t
        WHERE t.row_num > 1
    )
);
