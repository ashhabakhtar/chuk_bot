# 📊 CHUK Bot Visual Assets

![WhatsApp Chat Mockup](/C:/Users/Lenovo pc/.gemini/antigravity/brain/e95c2d70-116e-4f36-b341-a35e76bbf8b4/whatsapp_mockup_1776837227322.png)

Use these diagrams in your slides or documentation to explain how the system works.

## 1. System Architecture
This shows how the different parts of your project connect to each other.

```mermaid
graph TD
    User((User on WhatsApp)) -->|Sends Message| WA[WhatsApp Business API]
    WA -->|Webhook POST| Twilio[Twilio Gateway]
    Twilio -->|HTTPS Request| Ngrok[ngrok Tunnel]
    Ngrok -->|Local Traffic| Flask[Python Flask Server]
    
    subgraph "Local Machine / Server"
        Flask -->|Process Message| Handler[Chatbot Handler]
        Handler -->|SQL Query| DB[(MySQL Database)]
        DB -->|Product/User Data| Handler
        Handler -->|Generate Reply| Flask
    end
    
    Flask -->|TwiML XML Response| Twilio
    Twilio -->|Send Reply| WA
    WA -->|Delivers Message| User
```

---

## 2. The Registration Flow (Logic)
This explains the "Brain" of your chatbot and how it handles a new user.

```mermaid
sequenceDiagram
    participant U as User
    participant B as Bot
    participant D as Database

    U->>B: Sends "Hi"
    B->>D: Check if mobile exists in `users`
    D-->>B: User not found
    B->>U: "Welcome! What is your Full Name?"
    U->>B: "Ashhab Akhtar"
    B->>D: Save name in session
    B->>U: "Enter your Email Address"
    U->>B: "test@example.com"
    B->>D: Save user & Generate OTP
    B->>U: "OTP sent! Enter 6-digit code"
    U->>B: "123456"
    B->>U: "Verified! Here is your Main Menu..."
```

---

## 3. Database Schema Relation
How your tables are connected inside MySQL.

```mermaid
erDiagram
    USERS ||--o{ ORDERS : places
    USERS ||--o{ TICKETS : opens
    PRODUCTS ||--o{ ORDERS : contains
    USERS {
        string customer_id PK
        string name
        string mobile
        string email
    }
    PRODUCTS {
        int product_id PK
        string name
        string category
        float price
    }
    ORDERS {
        string order_id PK
        string customer_id FK
        int product_id FK
        int quantity
        string status
    }
```
