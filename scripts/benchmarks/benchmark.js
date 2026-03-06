const { v4: uuidv4 } = require('uuid');

function setup(client) {
  client.on('headers', (headers) => {
    // No changes needed to headers here
  });
}

function getBody() {
  return JSON.stringify({
    payment_id: uuidv4(),
    amount: (Math.random() * 1000).toFixed(2),
    currency: 'USD',
    recipient_email: 'bench@test.com',
    description: 'Benchmark Test'
  });
}

module.exports = {
  setup,
  getBody
};
