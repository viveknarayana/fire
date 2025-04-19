import React from "react";
import { Card, CardContent } from "@/components/ui/card";

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

export function FeatureCard({ icon, title, description }: FeatureCardProps) {
  return (
    <Card className="bg-black/40 border border-red-500/20 overflow-hidden hover:border-red-500/40 transition-all duration-300 group shadow-lg hover:shadow-red-500/5">
      <CardContent className="p-6">
        <div className="mb-4 transition-transform duration-500 group-hover:scale-110 group-hover:text-red-500">
          {icon}
        </div>
        <h3 className="text-xl font-bold mb-2">{title}</h3>
        <p className="text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
}