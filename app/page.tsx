import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { 
  Shield, 
  AlertTriangle, 
  Clock, 
  Map, 
  Cpu, 
  Video, 
  ArrowRight 
} from "lucide-react";
import { HeroSection } from "@/components/hero-section";
import { FeatureCard } from "@/components/feature-card";
import { StatCard } from "@/components/stat-card";

export default function Home() {
  return (
    <>
      <HeroSection />
      
      {/* Features Section */}
      <section id="features" className="py-24 bg-gradient-to-b from-black to-black/95">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-r from-red-500 to-red-700 bg-clip-text text-transparent">
              Advanced Fire Detection
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Our AI-powered system detects fires early, preventing catastrophic damage and saving lives.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <FeatureCard 
              icon={<AlertTriangle className="h-12 w-12 text-red-500" />}
              title="Early Detection"
              description="Detect fires at their earliest stages before they can spread and cause extensive damage."
            />
            <FeatureCard 
              icon={<Clock className="h-12 w-12 text-red-500" />}
              title="Real-time Alerts"
              description="Receive instant notifications when potential fire threats are detected in monitored areas."
            />
            <FeatureCard 
              icon={<Map className="h-12 w-12 text-red-500" />}
              title="Location Tracking"
              description="Precise location data helps emergency services respond quickly to the exact coordinates."
            />
            <FeatureCard 
              icon={<Cpu className="h-12 w-12 text-red-500" />}
              title="AI-Powered Analysis"
              description="Advanced algorithms analyze video feeds to distinguish between real fires and false alarms."
            />
            <FeatureCard 
              icon={<Video className="h-12 w-12 text-red-500" />}
              title="Video Processing"
              description="Process footage from various sources including drones, surveillance cameras, and user uploads."
            />
            <FeatureCard 
              icon={<Shield className="h-12 w-12 text-red-500" />}
              title="Preventive Measures"
              description="Identify high-risk areas and implement proactive fire prevention strategies."
            />
          </div>
        </div>
      </section>
      
      {/* Stats Section */}
      <section className="py-24 bg-gradient-to-b from-black/95 to-black relative overflow-hidden">
        <div className="absolute inset-0 bg-red-500/5 z-0"></div>
        <div className="container mx-auto px-4 relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-r from-red-500 to-red-700 bg-clip-text text-transparent">
              Making a Difference
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Firewatch is helping protect forests and communities around the world.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
            <StatCard number="95%" label="Detection Accuracy" />
            <StatCard number="30s" label="Average Detection Time" />
            <StatCard number="240+" label="Protected Areas" />
            <StatCard number="1.2M" label="Acres Safeguarded" />
          </div>
        </div>
      </section>
    </>
  );
}