import { Link, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { BarChart2, Settings, LineChart } from 'lucide-react';

const Navbar = () => {
  const location = useLocation();

  return (
    <nav className="border-b">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center">
            <span className="text-xl font-bold">AI对冲基金系统</span>
          </div>
          <div className="flex space-x-4">
            <Button
              variant={location.pathname === '/analysis' ? 'default' : 'ghost'}
              asChild
            >
              <Link to="/analysis" className="flex items-center space-x-2">
                <BarChart2 className="h-4 w-4" />
                <span>实时分析</span>
              </Link>
            </Button>
            <Button
              variant={location.pathname === '/backtest' ? 'default' : 'ghost'}
              asChild
            >
              <Link to="/backtest" className="flex items-center space-x-2">
                <LineChart className="h-4 w-4" />
                <span>回测</span>
              </Link>
            </Button>
            <Button
              variant={location.pathname === '/config' ? 'default' : 'ghost'}
              asChild
            >
              <Link to="/config" className="flex items-center space-x-2">
                <Settings className="h-4 w-4" />
                <span>配置</span>
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
