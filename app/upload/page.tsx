"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Upload, AlertTriangle, Check } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const { toast } = useToast();

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type.startsWith("video/")) {
        setFile(droppedFile);
      } else {
        toast({
          title: "Invalid file type",
          description: "Please upload a video file",
          variant: "destructive"
        });
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type.startsWith("video/")) {
        setFile(selectedFile);
      } else {
        toast({
          title: "Invalid file type",
          description: "Please upload a video file",
          variant: "destructive"
        });
      }
    }
  };

  const handleSubmit = () => {
    if (!file) {
      toast({
        title: "No file selected",
        description: "Please upload a video file first",
        variant: "destructive"
      });
      return;
    }

    setIsSubmitting(true);
    
    // Simulate upload process
    setTimeout(() => {
      setIsSubmitting(false);
      setIsSuccess(true);
      toast({
        title: "Alert Set Successfully",
        description: "We'll notify you if we detect any fire in this video",
        variant: "default"
      });
    }, 2000);
  };

  return (
    <div className="min-h-screen py-24 px-4 bg-gradient-to-b from-black to-red-950/30">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-r from-red-500 to-red-700 bg-clip-text text-transparent">
            Upload Video for Analysis
          </h1>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Submit your footage for AI-powered fire detection. Our system will analyze the video and alert you of any potential fire hazards detected.
          </p>
        </div>

        <Card className="border border-red-500/20 bg-black/40 shadow-lg shadow-red-500/5">
          <CardHeader>
            <CardTitle>Video Upload</CardTitle>
            <CardDescription>
              Upload video footage from forests, surveillance cameras, or drone flights
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div 
              className={`border-2 border-dashed rounded-lg p-12 text-center transition-all ${
                isDragging 
                  ? "border-red-500 bg-red-500/10" 
                  : file 
                    ? "border-green-500 bg-green-500/5" 
                    : "border-muted-foreground/25 hover:border-red-500/50 hover:bg-red-500/5"
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              {file ? (
                <div className="flex flex-col items-center">
                  <Check className="h-12 w-12 text-green-500 mb-4" />
                  <p className="font-medium text-lg mb-2">File Selected</p>
                  
                  <p className="text-sm text-muted-foreground mb-4">{file.name}</p>
                  <Button 
                    variant="outline" 
                    onClick={() => setFile(null)}
                    className="border-red-500/50 hover:border-red-500 hover:bg-red-500/10"
                  >
                    Change File
                  </Button>
                </div>
              ) : (
                <div className="flex flex-col items-center">
                  <Upload className="h-12 w-12 text-red-500 mb-4" />
                  <p className="font-medium text-lg mb-2">Drag and drop your video file</p>
                  <p className="text-sm text-muted-foreground mb-4">Or click to browse files</p>
                  <input
                    type="file"
                    accept="video/*"
                    className="hidden"
                    id="file-upload"
                    onChange={handleFileChange}
                  />
                  <label htmlFor="file-upload">
                    <Button 
                      variant="outline" 
                      className="cursor-pointer border-red-500/50 hover:border-red-500 hover:bg-red-500/10"
                      onClick={() => document.getElementById("file-upload")?.click()}
                    >
                      Browse Files
                    </Button>
                  </label>
                </div>
              )}
            </div>

            {file && (
              <div className="bg-black/60 rounded-lg p-6 border border-red-500/20">
                <h3 className="text-lg font-medium mb-4">File Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">File Name</p>
                    <p className="font-medium">{file.name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">File Size</p>
                    <p className="font-medium">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">File Type</p>
                    <p className="font-medium">{file.type}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Upload Date</p>
                    <p className="font-medium">{new Date().toLocaleDateString()}</p>
                  </div>
                </div>
              </div>
            )}

            <div className="flex flex-col items-center">
              <Button 
                onClick={handleSubmit}
                disabled={!file || isSubmitting || isSuccess}
                className={`w-full md:w-auto px-8 py-6 text-lg h-auto ${
                  isSuccess 
                    ? "bg-green-600 hover:bg-green-700" 
                    : "bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800"
                } shadow-lg shadow-red-500/20 transition-all duration-300 hover:shadow-red-500/40`}
              >
                {isSubmitting ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Processing...
                  </span>
                ) : isSuccess ? (
                  <span className="flex items-center">
                    <Check className="h-5 w-5 mr-2" />
                    Alert Set
                  </span>
                ) : (
                  <span className="flex items-center">
                    <AlertTriangle className="h-5 w-5 mr-2" />
                    Alert Me
                  </span>
                )}
              </Button>
              
              {isSuccess && (
                <p className="text-green-500 mt-4 text-center">
                  Video successfully uploaded and processed. We'll notify you if we detect any fires in this footage.
                </p>
              )}
            </div>
          </CardContent>
        </Card>
        
        <div className="mt-12 bg-black/40 border border-red-500/20 rounded-lg p-6 shadow-lg">
          <h2 className="text-xl font-bold mb-4">How It Works</h2>
          <ol className="space-y-4">
            <li className="flex">
              <div className="bg-gradient-to-r from-red-600 to-red-700 w-8 h-8 flex items-center justify-center rounded-full text-white font-bold mr-4 flex-shrink-0">1</div>
              <div>
                <h3 className="font-medium">Upload your video</h3>
                <p className="text-muted-foreground">Submit footage from forests, surveillance cameras, or drone flights</p>
              </div>
            </li>
            <li className="flex">
              <div className="bg-gradient-to-r from-red-600 to-red-700 w-8 h-8 flex items-center justify-center rounded-full text-white font-bold mr-4 flex-shrink-0">2</div>
              <div>
                <h3 className="font-medium">AI Analysis</h3>
                <p className="text-muted-foreground">Our advanced algorithms process the video to detect any signs of fire</p>
              </div>
            </li>
            <li className="flex">
              <div className="bg-gradient-to-r from-red-600 to-red-700 w-8 h-8 flex items-center justify-center rounded-full text-white font-bold mr-4 flex-shrink-0">3</div>
              <div>
                <h3 className="font-medium">Receive Alerts</h3>
                <p className="text-muted-foreground">Get immediate notifications if potential fire hazards are detected</p>
              </div>
            </li>
          </ol>
        </div>
      </div>
    </div>
  );
}