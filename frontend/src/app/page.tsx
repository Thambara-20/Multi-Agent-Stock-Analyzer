"use client";

import { useState, useEffect } from "react";
import { Button } from "./components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "./components/ui/card";
import { RefreshCw } from "lucide-react";

// Type for stock data
interface StockData {
  id: number;
  name: string;
  symbol: string;
  price: number;
  change: number;
}

// Mock data in case API fails
const MOCK_STOCKS: StockData[] = [
  { id: 1, name: "Apple Inc.", symbol: "AAPL", price: 150.45, change: 1.23 },
  {
    id: 2,
    name: "Microsoft Corporation",
    symbol: "MSFT",
    price: 280.67,
    change: -0.45,
  },
  {
    id: 3,
    name: "Amazon.com Inc.",
    symbol: "AMZN",
    price: 130.89,
    change: 0.78,
  },
  {
    id: 4,
    name: "Alphabet Inc.",
    symbol: "GOOGL",
    price: 120.32,
    change: -1.12,
  },
  { id: 5, name: "Tesla Inc.", symbol: "TSLA", price: 220.15, change: 2.34 },
];

export default function StockTracker() {
  const [stocks, setStocks] = useState<StockData[]>([]);
  const [loading, setLoading] = useState(false);

  // Function to fetch stock data from the backend
  const fetchStockData = async () => {
    setLoading(true);

    try {
      const response = await fetch("http://localhost:5000/analyze"); // Adjust URL as needed
      if (!response.ok) {
        throw new Error("Failed to fetch stock data");
      }

      const data = await response.json();

      // Transform API response to match UI format
      const formattedStocks: StockData[] = data.map(
        (stock: any, index: number) => ({
          id: index + 1,
          name: stock.name || stock.ticker, // Use name if available, otherwise ticker
          symbol: stock.ticker,
          price: stock.price || 0,
          change: stock.change || 0,
        })
      );

      setStocks(formattedStocks);
    } catch (error) {
      console.error(
        "Error fetching stock data, using mock data instead:",
        error
      );
      setStocks(MOCK_STOCKS); // Fallback to mock data if API call fails
    }

    setLoading(false);
  };

  // Fetch data on initial load
  useEffect(() => {
    fetchStockData();
  }, []);

  return (
    <div className="container mx-auto py-8 px-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-xl font-bold">
            Top 5 Stock Companies
          </CardTitle>
          <Button
            onClick={fetchStockData}
            disabled={loading}
            className="ml-auto"
          >
            {loading ? (
              <>
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                Refreshing...
              </>
            ) : (
              <>
                <RefreshCw className="mr-2 h-4 w-4" />
                Refresh
              </>
            )}
          </Button>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Company</TableHead>
                <TableHead>Symbol</TableHead>
                <TableHead className="text-right">Price ($)</TableHead>
                <TableHead className="text-right">Change (%)</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {stocks.map((stock) => (
                <TableRow key={stock.id}>
                  <TableCell className="font-medium">{stock.name}</TableCell>
                  <TableCell>{stock.symbol}</TableCell>
                  <TableCell className="text-right">
                    {stock.price.toFixed(2)}
                  </TableCell>
                  <TableCell
                    className={`text-right ${
                      stock.change >= 0 ? "text-green-600" : "text-red-600"
                    }`}
                  >
                    {stock.change >= 0 ? "+" : ""}
                    {stock.change.toFixed(2)}%
                  </TableCell>
                </TableRow>
              ))}
              {stocks.length === 0 && loading && (
                <TableRow>
                  <TableCell colSpan={4} className="text-center py-4">
                    Loading stock data...
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
