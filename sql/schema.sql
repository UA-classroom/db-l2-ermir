-- ==========================================
-- 1. CORE IDENTITY & AUTH
-- ==========================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    mobile_number VARCHAR(20) UNIQUE NOT NULL, -- Crucial for SMS auth
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_users_email ON users(email);

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL -- 'admin', 'provider', 'customer'
);

CREATE TABLE user_roles (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON user_roles(role_id);

CREATE TABLE user_addresses (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(20), -- 'home', 'work'
    street_address VARCHAR(255),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6)
);

-- ==========================================
-- 2. BUSINESS STRUCTURE
-- ==========================================

CREATE TABLE businesses (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    owner_id UUID REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    org_number VARCHAR(20) UNIQUE,
    slug VARCHAR(100) UNIQUE, -- 'nikita-hair'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_businesses_name_lower ON businesses(LOWER(name));
CREATE INDEX idx_businesses_slug ON businesses(slug);
CREATE INDEX idx_businesses_deleted_at ON businesses(deleted_at) WHERE deleted_at IS NULL;

CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    name VARCHAR(100), -- 'Stureplan Branch'
    address VARCHAR(255),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_locations_city ON locations(city);
CREATE INDEX idx_locations_deleted_at ON locations(deleted_at) WHERE deleted_at IS NULL;

CREATE TABLE location_contacts (
    id SERIAL PRIMARY KEY,
    location_id UUID REFERENCES locations(id) ON DELETE CASCADE,
    contact_type VARCHAR(50), -- 'Reception', 'Manager'
    phone_number VARCHAR(20)
);

-- ==========================================
-- 3. STAFF & SCHEDULES
-- ==========================================

CREATE TABLE employees (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    user_id UUID REFERENCES users(id), -- Nullable if placeholder, generally NOT NULL
    location_id UUID REFERENCES locations(id),
    job_title VARCHAR(100),
    bio TEXT,
    color_code VARCHAR(7), -- '#FF5733'
    is_active BOOLEAN DEFAULT TRUE,
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_employees_location_id ON employees(location_id);
CREATE INDEX idx_employees_is_active ON employees(is_active);
CREATE INDEX idx_employees_deleted_at ON employees(deleted_at) WHERE deleted_at IS NULL;

CREATE TABLE working_hours (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    employee_id UUID REFERENCES employees(id) ON DELETE CASCADE,
    day_of_week SMALLINT CHECK (day_of_week BETWEEN 1 AND 7), -- 1=Mon, 7=Sun
    start_time TIME,
    end_time TIME
    -- No unique constraint to allow split shifts
);

CREATE INDEX idx_working_hours_employee_day ON working_hours(employee_id, day_of_week);

CREATE TABLE internal_events (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    employee_id UUID REFERENCES employees(id) ON DELETE CASCADE,
    type VARCHAR(50), -- 'vacation', 'sick', 'meeting'
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    description TEXT
);

CREATE INDEX idx_internal_events_employee_time ON internal_events(employee_id, start_time, end_time);

-- ==========================================
-- 4. SERVICES & MENU
-- ==========================================

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    parent_id INTEGER REFERENCES categories(id),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE
);

CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE -- 'Vegan', 'Luxury'
);

CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_services_business_id ON services(business_id);

CREATE TABLE service_tags (
    service_id UUID REFERENCES services(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (service_id, tag_id)
);

CREATE TABLE service_variants (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    service_id UUID REFERENCES services(id) ON DELETE CASCADE,
    name VARCHAR(100), -- 'Long Hair', 'Student'
    price DECIMAL(10,2) NOT NULL,
    duration_minutes INTEGER NOT NULL
);

CREATE INDEX idx_service_variants_service_id ON service_variants(service_id);

CREATE TABLE employee_skills (
    employee_id UUID REFERENCES employees(id) ON DELETE CASCADE,
    service_variant_id UUID REFERENCES service_variants(id) ON DELETE CASCADE,
    custom_price DECIMAL(10,2), -- Override
    custom_duration INTEGER,    -- Override
    PRIMARY KEY (employee_id, service_variant_id)
);

CREATE INDEX idx_employee_skills_employee_id ON employee_skills(employee_id);
CREATE INDEX idx_employee_skills_variant_id ON employee_skills(service_variant_id);

-- ==========================================
-- 5. OPERATIONS (BOOKINGS & JOURNALS)
-- ==========================================

CREATE TABLE booking_statuses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    color_code VARCHAR(7),
    is_cancellable BOOLEAN DEFAULT TRUE
);

CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    customer_id UUID REFERENCES users(id),
    location_id UUID REFERENCES locations(id),
    employee_id UUID REFERENCES employees(id),
    service_variant_id UUID REFERENCES service_variants(id),
    status_id INTEGER REFERENCES booking_statuses(id),
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    total_price DECIMAL(10,2) NOT NULL, -- Snapshot price
    customer_note TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_bookings_start_time ON bookings(start_time);
CREATE INDEX idx_bookings_location_start ON bookings(location_id, start_time);
CREATE INDEX idx_bookings_customer_id ON bookings(customer_id);
CREATE INDEX idx_bookings_employee_id ON bookings(employee_id);
CREATE INDEX idx_bookings_status_id ON bookings(status_id);
CREATE INDEX idx_bookings_deleted_at ON bookings(deleted_at) WHERE deleted_at IS NULL;

CREATE TABLE journals (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    business_id UUID REFERENCES businesses(id), -- Linked to Brand for chain mobility
    customer_id UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE journal_entries (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    journal_id UUID REFERENCES journals(id) ON DELETE CASCADE,
    location_id UUID REFERENCES locations(id), -- Linked to specific shop for context
    employee_id UUID REFERENCES employees(id),
    booking_id UUID REFERENCES bookings(id),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==========================================
-- 6. COMMERCE (PRODUCTS & RETAIL)
-- ==========================================

CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    location_id UUID REFERENCES locations(id),
    name VARCHAR(100) NOT NULL,
    sku VARCHAR(50),
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0
);

CREATE TABLE inventory_logs (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    change_amount INTEGER NOT NULL, -- -1 or +50
    reason VARCHAR(50), -- 'sale', 'restock'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==========================================
-- 7. FINANCE & ORDERS
-- ==========================================

CREATE TABLE coupons (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    code VARCHAR(50) UNIQUE NOT NULL,
    discount_type VARCHAR(20) CHECK (discount_type IN ('percent', 'fixed')),
    discount_value DECIMAL(10,2) NOT NULL,
    usage_limit INTEGER,
    used_count INTEGER DEFAULT 0,
    valid_until TIMESTAMPTZ
);

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    customer_id UUID REFERENCES users(id),
    location_id UUID REFERENCES locations(id),
    coupon_id UUID REFERENCES coupons(id),
    total_amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'SEK',
    status VARCHAR(20) DEFAULT 'pending', -- 'paid', 'refunded'
    receipt_number VARCHAR(50) UNIQUE,
    receipt_url VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_location_id ON orders(location_id);

CREATE TABLE gift_cards (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    code VARCHAR(50) UNIQUE NOT NULL,
    initial_balance DECIMAL(10,2) NOT NULL,
    current_balance DECIMAL(10,2) NOT NULL,
    valid_until DATE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    -- Polymorphic / Exclusive Arc
    booking_id UUID REFERENCES bookings(id),
    product_id UUID REFERENCES products(id),
    gift_card_id UUID REFERENCES gift_cards(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    CONSTRAINT check_item_type CHECK (
        (booking_id IS NOT NULL)::int + 
        (product_id IS NOT NULL)::int + 
        (gift_card_id IS NOT NULL)::int = 1
    )
);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);

CREATE TABLE clipping_cards (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    customer_id UUID REFERENCES users(id),
    service_variant_id UUID REFERENCES service_variants(id),
    total_punches INTEGER NOT NULL,
    remaining_punches INTEGER NOT NULL,
    valid_until DATE
);

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'SEK',
    payment_method VARCHAR(50), -- 'klarna', 'card'
    status VARCHAR(20),
    transaction_id VARCHAR(100),
    gift_card_id UUID REFERENCES gift_cards(id), -- For split payments
    clipping_card_id UUID REFERENCES clipping_cards(id), -- For punches
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_payments_order_id ON payments(order_id);

-- ==========================================
-- 8. SOCIAL & NOTIFICATIONS
-- ==========================================

CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    booking_id UUID REFERENCES bookings(id) UNIQUE, -- Verified Review
    rating SMALLINT CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_reviews_booking_id ON reviews(booking_id);

CREATE TABLE favorites (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    location_id UUID REFERENCES locations(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, location_id)
);

CREATE TABLE notification_templates (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    slug VARCHAR(50) UNIQUE NOT NULL, -- 'booking-confirmed'
    channel VARCHAR(20), -- 'sms', 'email'
    subject_template VARCHAR(255),
    body_template TEXT
);

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    user_id UUID REFERENCES users(id),
    booking_id UUID REFERENCES bookings(id),
    template_id UUID REFERENCES notification_templates(id),
    status VARCHAR(20) DEFAULT 'pending', -- 'sent', 'failed'
    scheduled_at TIMESTAMPTZ,
    sent_at TIMESTAMPTZ,
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==========================================
-- 9. IMAGES & MEDIA
-- ==========================================

CREATE TABLE location_images (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    business_id UUID REFERENCES locations(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    alt_text VARCHAR(255),
    display_order INTEGER DEFAULT 0, -- For sorting (0 = primary image)
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_location_images_location_id ON location_images(location_id);

CREATE TABLE service_images (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    service_variant_id UUID REFERENCES service_variants(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    alt_text VARCHAR(255),
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_service_images_variant_id ON service_images(service_variant_id);

CREATE TABLE employee_images (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    employee_id UUID REFERENCES employees(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    alt_text VARCHAR(255),
    is_profile_picture BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_employee_images_employee_id ON employee_images(employee_id);
-- ==========================================