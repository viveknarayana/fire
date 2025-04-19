import { Card, CardContent } from "@/components/ui/card";

interface StatCardProps {
  number: string;
  label: string;
}

export function StatCard({ number, label }: StatCardProps) {
  return (
    <Card className="bg-black/40 border border-red-500/20 overflow-hidden hover:border-red-500/40 transition-all duration-300 group shadow-lg hover:shadow-red-500/5">
      <CardContent className="p-6 text-center">
        <div className="text-4xl font-bold mb-2 bg-gradient-to-r from-red-500 to-red-700 bg-clip-text text-transparent">
          {number}
        </div>
        <p className="text-muted-foreground">{label}</p>
      </CardContent>
    </Card>
  );
}