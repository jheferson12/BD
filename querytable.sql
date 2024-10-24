-----Obtener el menú con sus ingredientes (asumiendo que tienes una tabla menu_items y ingredients):-------

SELECT m.menu_id, m.name AS menu_name, i.name AS ingredient_name
FROM menus m
JOIN menu_items mi ON m.menu_id = mi.menu_id
JOIN ingredients i ON mi.ingredient_id = i.ingredient_id;
------------Total de ventas por cada elemento del menú (asumiendo una tabla orders y order_items):------------
SELECT m.name AS menu_name, SUM(oi.quantity) AS total_sales
FROM menus m
JOIN order_items oi ON m.menu_id = oi.menu_id
JOIN orders o ON oi.order_id = o.order_id
GROUP BY m.menu_id;
-------------Elementos del menú que no han sido ordenados nunca:----------------------
SELECT m.menu_id, m.name
FROM menus m
LEFT JOIN order_items oi ON m.menu_id = oi.menu_id
WHERE oi.menu_id IS NULL;
------------Promedio de precio de los elementos del menú por categoría----------------------
SELECT category, AVG(price) AS average_price
FROM menus
GROUP BY category;
---------Elementos del menú más vendidos en el último mes (enlazado con orders y order_items)-------
SELECT m.name AS menu_name, SUM(oi.quantity) AS total_sales
FROM menus m
JOIN order_items oi ON m.menu_id = oi.menu_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_date >= CURDATE() - INTERVAL 1 MONTH
GROUP BY m.menu_id
ORDER BY total_sales DESC;
-------------Detección de precios duplicados en el menú-------------------------
SELECT price, COUNT(*) AS occurrences
FROM menus
GROUP BY price
HAVING occurrences > 1