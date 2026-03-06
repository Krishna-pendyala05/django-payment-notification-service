const autocannon = require('autocannon');
const { v4: uuidv4 } = require('uuid');

async function runBenchmark() {
    const token = process.argv[2];
    const url = 'http://3.235.76.131:8000/api/v1/payments/';

    const instance = autocannon({
        url,
        connections: 5,
        duration: 20,
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        requests: [
            {
                method: 'POST',
                path: '/api/v1/payments/',
                setupRequest: (req, state) => {
                    req.body = JSON.stringify({
                        payment_id: uuidv4(),
                        amount: "10.00",
                        currency: "USD",
                        recipient_email: "bench@test.com",
                        description: "Benchmark Test"
                    });
                    return req;
                }
            }
        ]
    });

    autocannon.track(instance, { renderProgressBar: true });

    instance.on('done', (result) => {
        console.log('\n--- BENCHMARK RESULTS ---');
        console.log(JSON.stringify(result, null, 2));
    });
}

runBenchmark();
