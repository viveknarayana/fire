"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { fetchUserData } from "@/server/fetchData";
import { Button } from "@/components/ui/button";
import { Flame } from "lucide-react";
import { signOut } from "@/server/auth/actions";

// Define a type for the user (you may already have this defined elsewhere)
type User = {
  email?: string;
  // Add other user properties as needed
};

export function Navbar() {
  const pathname = usePathname();
  const [scrolled, setScrolled] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const handleScroll = () => {
      const offset = window.scrollY;
      if (offset > 50) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, []);

  useEffect(() => {
    const checkLoginStatus = async () => {
      try {
        const userData = await fetchUserData();
        if (userData && userData.user) {
          console.log("User data:", userData.user.email);
          setUser(userData.user);
          setIsLoggedIn(true);
         
        } else {
          setIsLoggedIn(false);
          setUser(null);
        }
      } catch (error) {
        console.error("Error checking login status:", error);
        setIsLoggedIn(false);
      }
    };

    checkLoginStatus();
  }, []);

  return (
    <header
      className={cn(
        "fixed top-0 w-full z-50 transition-all duration-300 border-b",
        scrolled
          ? "bg-black/90 backdrop-blur-sm border-red-500/20"
          : "bg-transparent border-transparent"
      )}
    >
      <div className="container flex h-16 items-center justify-between">
        <Link
          href="/"
          className="flex items-center space-x-2 transition-opacity hover:opacity-80"
        >
          <Flame className="h-8 w-8 text-red-500" />
          <span className="font-bold text-xl bg-gradient-to-r from-red-500 to-red-700 bg-clip-text text-transparent">
            Firewatch
          </span>
        </Link>
        <nav className="hidden md:flex items-center gap-6">
          <Link
            href="/"
            className={cn(
              "text-sm font-medium transition-colors hover:text-red-500",
              pathname === "/" ? "text-red-500" : "text-muted-foreground"
            )}
          >
            Home
          </Link>
          <Link
            href="/features"
            className={cn(
              "text-sm font-medium transition-colors hover:text-red-500",
              pathname === "/features" ? "text-red-500" : "text-muted-foreground"
            )}
          >
            Features
          </Link>
          <Link
            href="/about"
            className={cn(
              "text-sm font-medium transition-colors hover:text-red-500",
              pathname === "/about" ? "text-red-500" : "text-muted-foreground"
            )}
          >
            About
          </Link>
        </nav>
        <div className="flex items-center gap-4">
          {/* Always reserve space for the username */}
          
          
          {isLoggedIn ? (
            <>
              <Button
                variant="outline"
                className="border-red-500/30 text-white hover:bg-red-500/10 hover:text-red-400 transition-all duration-300"
                size="sm"
                onClick={async () => {
                  await signOut();
                  setIsLoggedIn(false);
                }}
              >
                Log Out
              </Button>
              <Link href="/upload">
                <Button
                  className="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 shadow-lg shadow-red-500/20 transition-all duration-300 hover:shadow-red-500/40"
                  size="sm"
                >
                  Upload File
                </Button>
              </Link>
            </>
          ) : (
            <Link href="/login">
              <Button
                variant="outline"
                className="border-red-500/30 text-white hover:bg-red-500/10 hover:text-red-400 transition-all duration-300"
                size="sm"
              >
                Log In
              </Button>
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}