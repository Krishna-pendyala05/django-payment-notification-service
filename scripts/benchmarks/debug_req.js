const axios = require('axios');
const { v4: uuidv4 } = require('uuid');

async function debug() {
  const token = process.argv[2];
  try {
    const resp = await axios.post('http://3.235.76.131:8000/api/v1/payments/', {
      payment_id: uuidv4(),
      amount: "10.00",
      currency: "USD",
      recipient_email: "bench@test.com",
      description: "Debug Test"
    }, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    console.log('Status:', resp.status);
    console.log('Body:', resp.data);
  } catch (err) {
    console.log('Error Status:', err.response?.status);
    console.log('Error Body:', err.response?.data);
  }
}

debug();
