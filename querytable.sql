----Obtener los detalles de todas las órdenes y la información de los productos:-------------------
SELECT od.order_detail_id, o.order_id, p.product_id, p.name AS product_name, od.quantity, od.price
FROM order_details od
JOIN orders o ON od.order_id = o.order_id
JOIN products p ON od.product_id = p.product_id;
-----------Total de ventas por producto:--------------------------
SELECT p.product_id, p.name AS product_name, SUM(od.quantity * od.price) AS total_sales
FROM order_details od
JOIN products p ON od.product_id = p.product_id
GROUP BY p.product_id;
----------------Detalles de las órdenes realizadas por un cliente específico:-------------------------
SELECT c.customer_id, c.name AS customer_name, o.order_id, od.product_id, p.name AS product_name, od.quantity, od.price
FROM order_details od
JOIN orders o ON od.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON od.product_id = p.product_id
WHERE c.email = 'example@example.com';
----------Productos que nunca se han ordenado:----------------------------
SELECT p.product_id, p.name
FROM products p
LEFT JOIN order_details od ON p.product_id = od.product_id
WHERE od.product_id IS NULL;
------------Cantidad total de cada producto vendido en el último mes:---------------------------
SELECT p.product_id, p.name AS product_name, SUM(od.quantity) AS total_quantity
FROM order_details od
JOIN orders o ON od.order_id = o.order_id
JOIN products p ON od.product_id = p.product_id
WHERE o.order_date >= CURDATE() - INTERVAL 1 MONTH
GROUP BY p.product_id
ORDER BY total_quantity DESC;
--------Precio promedio de los productos por categoría (asumiendo una tabla product_categories):--------------------
SELECT pc.category_name, AVG(od.price) AS average_price
FROM order_details od
JOIN products p ON od.product_id = p.product_id
JOIN product_categories pc ON p.category_id = pc.category_id
GROUP BY total_quantity DESC;
