import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './Layout';
import Dashboard from './pages/Dashboard';
import MemberProfile from './pages/MemberProfile';
import MembersList from './pages/MembersList';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/members" element={<MembersList />} />
          <Route path="/member/:id" element={<MemberProfile />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
