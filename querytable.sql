----------Obtener los detalles de todas las órdenes y la información de los productos:--------------------
SELECT od.order_detail_id, o.order_id, p.product_id, p.name AS product_name, od.quantity, od.price
FROM order_details od
JOIN orders o ON od.order_id = o.order_id
JOIN products p ON od.product_id = p.product_id;
-------------------------Total de ventas por producto:--------------------------------------
SELECT p.product_id, p.name AS product_name, SUM(od.quantity * od.price) AS total_sales
FROM order_details od
JOIN products p ON od.product_id = p.product_id
GROUP BY p.product_id;
-----------------Detalles de las órdenes realizadas por un cliente específico:-------------------------
SELECT c.customer_id, c.name AS customer_name, o.order_id, od.product_id, p.name AS product_name, od.quantity, od.price
FROM order_details od
JOIN orders o ON od.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON od.product_id = p.product_id
WHERE c.email = 'example@example.com';
----------------Productos que nunca se han ordenado:-----------------------
SELECT p.product_id, p.name
FROM products p
LEFT JOIN order_details od ON p.product_id = od.product_id
WHERE od.product_id IS NULL;
------------Cantidad total de cada producto vendido en el último mes:-----------------------
SELECT p.product_id, p.name AS product_name, SUM(od.quantity) AS total_quantity
FROM order_details od
JOIN orders o ON od.order_id = o.order_id
JOIN products p ON od.product_id = p.product_id
WHERE o.order_date >= CURDATE() - INTERVAL 1 MONTH
GROUP BY p.product_id
ORDER BY total_quantity DESC;
----------------Precio promedio de los productos por categoría (asumiendo una tabla product_categories):-------------------
SELECT pc.category_name, AVG(od.price) AS average_price
FROM order_details od
JOIN products p ON od.product_id = p.product_id
JOIN product_categories pc ON p.category_id = pc.category_id
GROUP
-------------Obtener todos los elementos del menú con sus categorías (asumiendo una tabla menu_categories):----------------
SELECT um.uploadmenu_id, um.name AS menu_name, mc.category_name
FROM uploadmenu um
JOIN menu_categories mc ON um.category_id = mc.category_id;
--------------Total de veces que cada elemento del menú ha sido ordenado (asumiendo una tabla order_items):----------------
SELECT um.uploadmenu_id, um.name AS menu_name, SUM(oi.quantity) AS total_orders
FROM uploadmenu um
JOIN order_items oi ON um.uploadmenu_id = oi.menu_id
GROUP BY um.uploadmenu_id;
------------------Elementos del menú que nunca han sido ordenados:----------------------
SELECT um.uploadmenu_id, um.name
FROM uploadmenu um
LEFT JOIN order_items oi ON um.uploadmenu_id = oi.menu_id
WHERE oi.menu_id IS NULL;
---------------Precio promedio de los elementos del menú por categoría (asumiendo una tabla menu_categories):-------------------
SELECT mc.category_name, AVG(um.price) AS average_price
FROM uploadmenu um
JOIN menu_categories mc ON um.category_id = mc.category_id
GROUP BY mc.category_name;
--------------Elementos del menú subidos en los últimos 30 días:-----------------------------
SELECT um.uploadmenu_id, um.name, um.upload_date
FROM uploadmenu um
WHERE um.upload_date >= CURDATE() - INTERVAL 30 DAY;
-------------Detectar elementos duplicados en el menú (por nombre):--------------------------
SELECT um.name, COUNT(*) AS occurrences
FROM uploadmenu um
GROUP BY um.name
HAVING occurrences > 1;
