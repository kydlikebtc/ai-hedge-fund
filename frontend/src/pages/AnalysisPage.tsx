import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { Toaster } from '@/components/ui/toaster';

interface MarketData {
  price: number;
  change24h: number;
  volume: number;
}

interface AgentAnalysis {
  title: string;
  content: string;
  loading: boolean;
}

const AnalysisPage = () => {
  const { toast } = useToast();
  const [cryptocurrencies, setCryptocurrencies] = useState<Array<{ symbol: string; name: string }>>([]);
  const [selectedCrypto, setSelectedCrypto] = useState<string>("BTC");
  const [marketData, setMarketData] = useState<MarketData>({
    price: 0,
    change24h: 0,
    volume: 0,
  });

  const [agents, setAgents] = useState<AgentAnalysis[]>([
    { title: '市场数据代理', content: '价格趋势分析显示BTC处于盘整阶段...', loading: false },
    { title: '情绪代理', content: '市场情绪偏向谨慎，社交媒体讨论热度适中...', loading: false },
    { title: '技术代理', content: 'RSI指标显示超卖，MACD即将形成金叉...', loading: false },
    { title: '风险代理', content: '当前市场波动性较高，建议控制仓位...', loading: false },
    { title: '投资组合代理', content: '建议当前仓位保持在30%，等待更好的入场机会...', loading: false },
  ]);

  const [loading, setLoading] = useState(false);

  const fetchCryptocurrencies = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/cryptocurrencies');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setCryptocurrencies(data.data);
    } catch (error) {
      console.error('Error fetching cryptocurrencies:', error);
      toast({
        title: "错误",
        description: "获取加密货币列表失败，请稍后重试",
        variant: "destructive",
      });
    }
  };

  useEffect(() => {
    fetchCryptocurrencies();
  }, []);

  const refreshAnalysis = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/market-data/${selectedCrypto}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setMarketData(data);

      const analysisResponse = await fetch(`http://localhost:8000/api/analysis/${selectedCrypto}`);
      if (!analysisResponse.ok) {
        throw new Error(`HTTP error! status: ${analysisResponse.status}`);
      }
      const analysisData = await analysisResponse.json();
      setAgents(analysisData.agents);
    } catch (error) {
      console.error('Failed to refresh analysis:', error);
      toast({
        title: "错误",
        description: "更新市场数据失败，请稍后重试",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshAnalysis();
  }, [selectedCrypto]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">{selectedCrypto}市场分析</h1>
        <div className="flex items-center gap-4">
          <Select value={selectedCrypto} onValueChange={setSelectedCrypto}>
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="选择加密货币" />
            </SelectTrigger>
            <SelectContent>
              {cryptocurrencies.map((crypto) => (
                <SelectItem key={crypto.symbol} value={crypto.symbol}>
                  {crypto.name} ({crypto.symbol})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button onClick={refreshAnalysis} disabled={loading}>
            {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
            刷新数据
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>市场数据</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground">价格</p>
              <p className="text-2xl font-bold">${marketData.price.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">24小时涨跌</p>
              <p className={`text-2xl font-bold ${marketData.change24h >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                {marketData.change24h.toFixed(2)}%
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">成交量</p>
              <p className="text-2xl font-bold">${marketData.volume.toFixed(1)}B</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-4">
        <h2 className="text-2xl font-bold">AI代理分析</h2>
        {agents.map((agent, index) => (
          <Card key={index}>
            <CardHeader>
              <CardTitle>{agent.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">{agent.content}</p>
            </CardContent>
          </Card>
        ))}
      </div>
      <Toaster />
    </div>
  );
};

export default AnalysisPage;
