SELECT
    o.order_id,
    c.name AS customer_name,
    o.order_date,
    SUM(oi.quantity * oi.unit_price) AS total_amount,
    p.payment_method
FROM orders AS o
JOIN customers AS c
    ON c.customer_id = o.customer_id
JOIN order_items AS oi
    ON oi.order_id = o.order_id
JOIN payments AS p
    ON p.order_id = o.order_id
GROUP BY
    o.order_id,
    c.name,
    o.order_date,
    p.payment_method
ORDER BY
    total_amount DESC
LIMIT 20;
