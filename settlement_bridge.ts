import { ethers } from 'ethers';
import axios from 'axios';

const RPC_URL = process.env.RPC_URL || '';
const ESCROW_ADDRESS = process.env.ESCROW_ADDRESS || '';
const CIRCLE_API = 'https://api.circle.com/v1';
const BANK_WEBHOOK = process.env.BANK_WEBHOOK || '';
const provider = new ethers.JsonRpcProvider(RPC_URL);

const escrowAbi = [
  'event Deposited(address indexed from, uint256 amount)',
  'event Swapped()',
  'event Refunded()'
];

const escrow = new ethers.Contract(ESCROW_ADDRESS, escrowAbi, provider);

async function postWithRetry(url: string, data: any, retries = 5) {
  let delay = 1000;
  for (let i = 0; i < retries; i++) {
    try {
      await axios.post(url, data);
      return;
    } catch (e) {
      await new Promise(r => setTimeout(r, delay));
      delay *= 2;
    }
  }
}

escrow.on('Swapped', async () => {
  try {
    await axios.post(`${CIRCLE_API}/cctp/mint`, { amount: '100' });
    const xml = `<Payment><Amt>100</Amt></Payment>`;
    await postWithRetry(BANK_WEBHOOK, xml);
  } catch (e) {
    console.error('bridge error', e);
  }
});

escrow.on('Refunded', async () => {
  console.log('Swap refunded');
});

console.log('bridge listening');
