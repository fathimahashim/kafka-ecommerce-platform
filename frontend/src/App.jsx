import { useState } from 'react'
import './App.css'

const API_URL = 'http://127.0.0.1:8001'

function App() {
  const [form, setForm] = useState({
    customer_email: '',
    product: '',
    quantity: 1,
    amount: ''
  })
  const [order, setOrder] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [timedOut, setTimedOut] = useState(false)

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    setOrder(null)
    setTimedOut(false)

    try {
      const res = await fetch(`${API_URL}/orders`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          quantity: Number(form.quantity),
          amount: Number(form.amount)
        })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Something went wrong')
      pollOrderStatus(data.order_id)
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  const pollOrderStatus = (orderId) => {
    let attempts = 0
    const interval = setInterval(async () => {
      attempts += 1
      const res = await fetch(`${API_URL}/orders/${orderId}`)
      const data = await res.json()
      setOrder(data)

      if (data.status === 'paid' || data.status === 'failed') {
        clearInterval(interval)
        setLoading(false)
      } else if (attempts >= 15) {
        clearInterval(interval)
        setLoading(false)
        setTimedOut(true)
      }
    }, 1000)
  }

  return (
    <div className="page">
      <nav className="nav">
        <span className="brand">Kafka<span className="brand-accent">Mart</span></span>
        <span className="badge">● Live Kafka Demo</span>
      </nav>

      <header className="hero">
        <div className="hero-inner">
          <p className="eyebrow">Event-driven checkout</p>
          <h1>Every order tells<br />a story in real time.</h1>
          <p className="hero-sub">
            Place an order below and watch it move through a live Kafka pipeline —
            from checkout to confirmed payment, streamed to you as it happens.
          </p>
          <a className="scroll-cue" href="#console">See it live ↓</a>
        </div>
      </header>

      <main id="console" className="console">
        <section className="checkout-card">
          <h2>Checkout</h2>
          <form onSubmit={handleSubmit}>
            <label>
              Email
              <input type="email" name="customer_email" placeholder="you@example.com" value={form.customer_email} onChange={handleChange} required />
            </label>
            <label>
              Product
              <input type="text" name="product" placeholder="e.g. Running shoes" value={form.product} onChange={handleChange} required />
            </label>
            <div className="row">
              <label>
                Quantity
                <input type="number" name="quantity" min="1" value={form.quantity} onChange={handleChange} required />
              </label>
              <label>
                Amount ($)
                <input type="number" name="amount" min="0" step="0.01" placeholder="0.00" value={form.amount} onChange={handleChange} required />
              </label>
            </div>
            <button type="submit" disabled={loading}>
              {loading ? 'Processing…' : 'Place order'}
            </button>
          </form>
          {error && <p className="error">{error}</p>}
        </section>

        <section className="receipt-wrap">
          <h2>Order receipt</h2>
          {!order && <p className="receipt-placeholder">Your order will appear here the moment it's placed.</p>}
          {order && (
            <div className={`receipt status-${order.status}`}>
              <div className="receipt-row"><span>Order</span><span>#{order.id}</span></div>
              <div className="receipt-row"><span>Product</span><span>{order.product}</span></div>
              <div className="receipt-row"><span>Qty</span><span>{order.quantity}</span></div>
              <div className="receipt-row"><span>Amount</span><span>${Number(order.amount).toFixed(2)}</span></div>
              <div className="receipt-divider" />
              <div className="receipt-status">
                {order.status === 'pending' && <span className="dot pulse" />}
                <span className="status-text">{order.status}</span>
              </div>
              {order.status === 'paid' && <div className="stamp">PAID</div>}
              {timedOut && order.status === 'pending' && (
                <p className="timeout-note">Still processing — check that payment-service is running.</p>
              )}
            </div>
          )}
        </section>
      </main>

      <section className="how">
        <h2>How this works</h2>
        <div className="steps">
          <div className="step">
            <span className="step-num">01</span>
            <h3>Order placed</h3>
            <p>The checkout API saves your order and responds immediately — no waiting.</p>
          </div>
          <div className="step">
            <span className="step-num">02</span>
            <h3>Event published</h3>
            <p>An <code>order_placed</code> event is sent to Kafka for any service that needs it.</p>
          </div>
          <div className="step">
            <span className="step-num">03</span>
            <h3>Processed independently</h3>
            <p>Payment, email, and analytics services each react on their own — this receipt shows payment.</p>
          </div>
        </div>
      </section>

      <footer className="footer">
        <p>Built with FastAPI · Apache Kafka · PostgreSQL · React</p>
        <a href="https://github.com/fathimahashim" target="_blank" rel="noreferrer">View source on GitHub</a>
      </footer>
    </div>
  )
}

export default App