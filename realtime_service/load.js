import http from 'k6/http';

export const options = {
  scenarios: {
    load: {
      executor: 'constant-arrival-rate',
      rate: 1000,
      timeUnit: '1s',
      duration: '10s',
      preAllocatedVUs: 50,
    },
  },
};

export default function () {
  http.get('http://localhost:8000/score/TEST');
}
