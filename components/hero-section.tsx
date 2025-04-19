import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

export function HeroSection() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
      {/* Background Animation */}
      <div className="absolute inset-0 z-0">
        <div className="absolute inset-0 bg-black"></div>
        <div className="absolute -inset-[10%] opacity-30 blur-3xl bg-gradient-to-br from-red-500 to-red-700 animate-pulse" style={{ animationDuration: '8s' }}></div>
      </div>
      
      {/* Video Background */}
      <div className="absolute inset-0 z-0 opacity-30">
        <video
          autoPlay
          loop
          muted
          playsInline
          className="object-cover h-full w-full"
        >
          <source src="https://assets.mixkit.co/videos/preview/mixkit-forest-fire-spreading-5750-large.mp4" type="video/mp4" />
        </video>
        <div className="absolute inset-0 bg-black/70"></div>
      </div>
      
      {/* Content */}
      <div className="container relative z-10">
        <div className="max-w-3xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 leading-tight">
            <span className="bg-gradient-to-r from-red-500 to-red-700 bg-clip-text text-transparent">
              Detecting Fires
            </span>
            <br />
            <span className="text-white">Before They Spread</span>
          </h1>
          <p className="text-lg md:text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Firewatch uses advanced AI technology to detect wildfires at their earliest stages, 
            helping to protect forests, wildlife, and communities.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/upload">
              <Button className="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 shadow-lg shadow-red-500/20 transition-all duration-300 hover:shadow-red-500/40 text-white px-8 py-6 text-lg h-auto">
                Upload Video
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link href="#features">
              <Button variant="outline" className="border-red-500/50 hover:border-red-500 text-white hover:bg-red-500/10 px-8 py-6 text-lg h-auto">
                Learn More
              </Button>
            </Link>
          </div>
        </div>
      </div>
      
      {/* Bottom Gradient */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-black to-transparent z-10"></div>
    </section>
  );
}