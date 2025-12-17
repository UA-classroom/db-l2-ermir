export interface Product {
    id: string;
    location_id: string;
    name: string;
    sku?: string;
    price: number;
    stock_quantity: number;
}

export interface ProductCreate {
    location_id: string;
    name: string;
    sku?: string; // Optional
    price: number;
    stock_quantity: number;
}

export interface ProductUpdate {
    name?: string;
    sku?: string;
    price?: number;
    stock_quantity?: number;
}
