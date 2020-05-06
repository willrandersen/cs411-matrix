SELECT * FROM celebrities
WHERE firstname LIKE '%%{}%%' OR lastname LIKE '%%{}%%' OR CONCAT(firstname, ' ', lastname) LIKE '%%{}%%'
ORDER BY numberoffans DESC, id