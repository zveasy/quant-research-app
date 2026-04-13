const express = require('express');
const app = express();

app.get('/healthz', (_req, res) => res.json({ status: 'ok' }));
app.get('/', (_req, res) => {
  res.send('Quant Research Dashboard placeholder');
});

app.listen(3000, () => console.log('dashboard listening on 3000'));
