import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface ApiKeys {
  openai: string;
  anthropic: string;
  coinmarketcap: string;
}

const ConfigPage = () => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [apiKeys, setApiKeys] = useState<ApiKeys>({
    openai: '',
    anthropic: '',
    coinmarketcap: '',
  });

  const handleInputChange = (key: keyof ApiKeys) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setApiKeys(prev => ({
      ...prev,
      [key]: e.target.value,
    }));
  };

  const testConnection = async () => {
    setLoading(true);
    try {
      // TODO: Implement API connection test
      await new Promise(resolve => setTimeout(resolve, 1500));
      toast({
        title: '连接测试成功',
        description: '所有API密钥验证通过',
      });
    } catch (error) {
      toast({
        title: '连接测试失败',
        description: '请检查API密钥是否正确',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const saveConfig = async () => {
    setLoading(true);
    try {
      // TODO: Implement config saving
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast({
        title: '配置保存成功',
        description: 'API密钥已更新',
      });
    } catch (error) {
      toast({
        title: '配置保存失败',
        description: '请稍后重试',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">系统配置</h1>

      <Card>
        <CardHeader>
          <CardTitle>API密钥配置</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">OpenAI API Key</label>
              <Input
                type="password"
                value={apiKeys.openai}
                onChange={handleInputChange('openai')}
                placeholder="sk-..."
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Anthropic API Key</label>
              <Input
                type="password"
                value={apiKeys.anthropic}
                onChange={handleInputChange('anthropic')}
                placeholder="sk-ant-..."
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">CoinMarketCap API Key</label>
              <Input
                type="password"
                value={apiKeys.coinmarketcap}
                onChange={handleInputChange('coinmarketcap')}
              />
            </div>
          </div>

          <div className="flex space-x-4">
            <Button onClick={testConnection} disabled={loading}>
              {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              测试连接
            </Button>
            <Button onClick={saveConfig} disabled={loading}>
              {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              保存配置
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ConfigPage;
