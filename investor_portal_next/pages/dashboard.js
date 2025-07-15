import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis } from 'recharts';
import { withPageAuthRequired } from '@auth0/nextjs-auth0/client';

export default withPageAuthRequired(function Dashboard({ data }) {
  return (
    <LineChart width={600} height={300} data={data}>
      <XAxis dataKey="date" />
      <YAxis />
      <Line type="monotone" dataKey="value" stroke="#8884d8" />
    </LineChart>
  );
});

export async function getServerSideProps() {
  const res = await fetch('http://localhost:8000/v1/perf');
  const data = await res.json();
  return { props: { data } };
}
