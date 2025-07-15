export default async function handler(req, res) {
  const resp = await fetch('http://localhost:8000/tearsheet.pdf');
  const buf = await resp.arrayBuffer();
  res.setHeader('Content-Type', 'application/pdf');
  res.send(Buffer.from(buf));
}
