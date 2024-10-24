-------------------obtiene informacion cliente especifico por correo-------------------------------------------------------------------------
SELECT * 
FROM customers 
WHERE email = 'example@example.com';
-------------------pedidos realizados por cada cliente------------------------------------------------------------------------------
SELECT c.customer_id, c.name, o.order_id, o.order_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
ORDER BY c.customer_id;
-------------------clientes que no han hecho pedidos------------------------------------------------------------------------------
SELECT c.customer_id, c.name, c.email 
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL
-------------------cuenta total de pedidos realizados menor a mayor-----------------------------------------------------------------------------
SELECT c.customer_id, c.name, COUNT(o.order_id) AS total_orders
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id
ORDER BY total_orders DESC;
---------------------muestra clientes que realizaron pedidos ultimos 30 dias---------------------------------------------------------------------------
SELECT c.customer_id, c.name, o.order_date
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date >= CURDATE() - INTERVAL 30 DAY;
--------------------detecta si hay registros detectados----------------------------------------------------------------------------
SELECT email, COUNT(*) AS occurrences 
FROM customers 
GROUP BY email 
HAVING occurrences > 1;
---------------------cliente que ha pedido mas items en total---------------------------------------------------------------------------
SELECT c.customer_id, c.name, SUM(od.quantity) AS total_items_ordered 
FROM customers c 
JOIN orders o ON c.customer_id = o.customer_id 
JOIN order_details od ON o.order_id = od.order_id 
GROUP BY c.customer_id 
ORDER BY total_items_ordered DESC 
LIMIT 1;
-------------------------------------------------------------------------------------------------
