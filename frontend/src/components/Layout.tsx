import type { ReactNode } from 'react';
//import Navbar from './Navbar';
interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div>
      <main className="p-6">{children}</main>
    </div>
  );
};

export default Layout;