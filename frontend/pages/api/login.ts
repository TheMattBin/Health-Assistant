// Next.js API route for login (mock, replace with real backend call)
import type { NextApiRequest, NextApiResponse } from 'next';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    const { username, password } = req.body;
    // Replace this with real authentication logic (e.g., call FastAPI backend)
    if (username === 'admin' && password === 'password') {
      // Set a cookie or token here for real auth
      res.status(200).json({ message: 'Login successful' });
    } else {
      res.status(401).json({ message: 'Invalid credentials' });
    }
  } else {
    res.status(405).json({ message: 'Method not allowed' });
  }
}
