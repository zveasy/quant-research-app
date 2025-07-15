import init, { smooth } from './smoothed_score.js';

async function run() {
  await init();
  console.log(smooth(10, 0.5));
}
run();
