db = db.getSiblingDB('demo_db');

db.createCollection('products');

db.products.insertMany([
    {
        name: "Wireless Noise-Canceling Headphones",
        category: "Electronics",
        price: 299.99,
        description: "Premium over-ear headphones with active noise cancellation."
    },
    {
        name: "Smartphone X Pro",
        category: "Electronics",
        price: 999.00,
        description: "Latest flagship smartphone with high-resolution camera."
    },
    {
        name: "4K Ultra HD Monitor",
        category: "Electronics",
        price: 450.50,
        description: "27-inch monitor perfect for gaming and professional work."
    },
    {
        name: "Ergonomic Office Chair",
        category: "Furniture",
        price: 199.99,
        description: "Comfortable chair with lumbar support for long working hours."
    },
    {
        name: "Stainless Steel Water Bottle",
        category: "Accessories",
        price: 25.00,
        description: "Insulated bottle keeps drinks cold for 24 hours."
    },
    {
        name: "Bluetooth Speaker",
        category: "Electronics",
        price: 79.99,
        description: "Portable speaker with deep bass and long battery life."
    }
]);
