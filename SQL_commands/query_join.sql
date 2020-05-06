SELECT * FROM celebrities c, media m
WHERE c.gender = '{}' AND c.age >= '{}' AND c.age <= '{}' AND c.height >= '{}' AND c.height <= '{}'  AND c.weight >= '{}' AND c.weight <= '{}'
AND m.type = '{}' AND m.celeb_id = c.id
ORDER BY c.id;
