# Finance Project

# Real-Time Stock Simulator & WebSocket Playground

A web app that lets you practice trading stocks in real time with fake money, while demonstrating how modern websites stream live financial data without constantly refreshing the page.

---

## What Does This Project Do?

1. **Streams Live Stock Prices:** Pulls current market prices using the Twelve Data API and Yahoo Finance, streaming them straight to your screen the second they change.
2. **Lets You "Paper Trade":** Gives you a simulated cash balance ($100,000) so you can buy and sell shares of real companies risk-free.
3. **Shows How WebSockets Work:** Instead of the browser repeatedly asking the server *"Is there a new price yet?"* every second (traditional polling), the server keeps an open connection and pushes updates the millisecond they happen.

---

## Why Did I Build This?

Most beginner tutorials only cover basic REST APIs (where the user clicks a button and waits for a response). But real-world financial platforms—like Robinhood, Binance, or Bloomberg—can't work that way; prices change multiple times a second.

This project was built to get hands-on experience with:
* Keeping a live, two-way connection open between the browser and the server using **WebSockets**.
* Managing high-speed incoming data without freezing or lagging the browser.
* Handling real trading logic: tracking buy/sell orders, updating portfolios, and calculating profits and losses on the fly.

---

## Tech Stack & How It Fits Together

* **TypeScript & HTML (Frontend):** Builds the dashboard you see in the browser. It listens for incoming price ticks, updates the live charts smoothly, and lets you submit buy/sell orders.
* **Python & Flask-SocketIO (Backend):** The brain of the project. It connects to financial APIs to get live prices, manages user accounts, and broadcasts the live updates to everyone viewing the page.
* **PostgreSQL & SQLAlchemy (Database):** Safely stores user login info, current stock holdings, and trade history.
* **C (Performance Engine):** Used for low-level, high-speed calculations (like matching orders or crunching math heavy portfolio numbers instantly).

---

## How It Works Behind the Scenes

```text
[Twelve Data / Yahoo Finance]
             │  (Live market quotes)
             ▼
      [Flask Backend]  ◄──►  [C Module] (Fast math / order checks)
             │
             ├── Saves trades to PostgreSQL database
             │
             ▼  (WebSocket stream: sends new prices instantly)
     [Your Web Browser]
      (Updates charts, balance, and holdings on screen)
## Credit

Logos - https://github.com/davidepalazzo/ticker-logos


