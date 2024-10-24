---------Obtener todas las órdenes y sus detalles de los clientes:---------------
SELECT o.order_id, o.order_date, c.customer_id, c.name AS customer_name
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id;
----------Total de ventas por cliente:---------------
SELECT c.customer_id, c.name AS customer_name, SUM(oi.quantity * oi.price) AS total_sales
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id;
-----------Órdenes que contienen un producto específico (asumiendo una tabla products):-------------
SELECT o.order_id, o.order_date, p.product_id, p.name AS product_name
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE p.name = 'example_product';
----------Total de órdenes por cada día del mes:------------------
SELECT DATE(order_date) AS order_day, COUNT(order_id) AS total_orders
FROM orders
GROUP BY order_day;
--------Órdenes realizadas en el último mes:-----------------
SELECT * FROM orders
WHERE order_date >= CURDATE() - INTERVAL 1 MONTH;
------Productos más vendidos en el último mes (enlazado con order_items y products)------------
SELECT p.product_id, p.name AS product_name, SUM(oi.quantity) AS total_quantity
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_date >= CURDATE() - INTERVAL 1 MONTH
GROUP BY p.product_id
ORDER BY total_quantity DESC;