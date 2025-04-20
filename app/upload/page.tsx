"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Upload, Check } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { Progress } from "@/components/ui/progress";
import { fetchUserData } from "@/server/fetchData";

type User = {
  email?: string;
  uuid?: string;
  // Add other user properties as needed
};

export default function VideoProcessor() {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processProgress, setProcessProgress] = useState(0);
  const [totalFrames, setTotalFrames] = useState(0);
  const [processedFrames, setProcessedFrames] = useState(0);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [userUuid, setUserUuid] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const processingRef = useRef<boolean>(false);
  const { toast } = useToast();

  useEffect(() => {
    // Fetch user data when component mounts
    const getUserData = async () => {
      try {
        const userData = await fetchUserData();
        console.log("User data fetched:", userData);

        if (userData && userData.user) {
          console.log("User data:", userData.user.email);
          setUser(userData.user);
        
        if (userData.user?.email) {
          setUserEmail(userData.user.email);
        }
        
        if (userData.user?.id) {
          setUserUuid(userData.user.id);
        } 
      }
      } 
      catch (error) {
        console.error("Error fetching user data:", error);
        toast({
          title: "Authentication Error",
          description: "Failed to fetch user data. Please try logging in again.",
          variant: "destructive"
        });
      }
    };
    
    getUserData();
    
    return () => {
      processingRef.current = false;
    };
  }, [toast]);

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

  const processVideo = async (videoFile: File): Promise<void> => {
    return new Promise<void>((resolve, reject) => {
      try {
        const video = videoRef.current;
        const canvas = canvasRef.current;
        
        if (!video || !canvas) {
          reject(new Error("Video or canvas element not available"));
          return;
        }

        if (!userUuid) {
          reject(new Error("User authentication required"));
          return;
        }
        
        processingRef.current = true;
        const videoURL = URL.createObjectURL(videoFile);
        video.src = videoURL;
        
        video.onloadedmetadata = () => {
          setProcessedFrames(0);
          const frameStep = 10; // Process every 10th frame
          const totalEstimatedFrames = Math.floor(video.duration * 30) / frameStep; // Assuming 30fps
          setTotalFrames(totalEstimatedFrames);
          
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          const ctx = canvas.getContext('2d');
          
          if (!ctx) {
            reject(new Error("Could not get canvas context"));
            return;
          }
          
          video.oncanplay = async () => {
            let framesProcessed = 0;
            let frameCounter = 0;
            
            const processFrames = async () => {
              try {
                if (!processingRef.current) {
                  URL.revokeObjectURL(videoURL);
                  resolve();
                  return;
                }
                
                const frameTime = (frameCounter * frameStep) / 30;
                
                if (frameTime >= video.duration) {
                  processingRef.current = false;
                  URL.revokeObjectURL(videoURL);
                  toast({
                    title: "Processing Complete",
                    description: `All ${framesProcessed} frames have been processed`,
                  });
                  resolve();
                  return;
                }
                
                video.currentTime = frameTime;
                
                await new Promise<void>((seekResolve) => {
                  const onSeeked = () => {
                    video.removeEventListener('seeked', onSeeked);
                    seekResolve();
                  };
                  video.addEventListener('seeked', onSeeked);
                });
                
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

                const imageDataUrl = canvas.toDataURL('image/jpeg', 0.8);
                
                // Update counters and progress
                framesProcessed++;
                frameCounter++;
                setProcessedFrames(framesProcessed);
                setProcessProgress(Math.min(100, Math.floor((frameTime / video.duration) * 100)));
                
                // Show notification every 50 frames processed
                if (framesProcessed % 20 === 0) {
                  console.log(`Processed frame ${framesProcessed} at time ${frameTime.toFixed(2)} seconds`);
                  canvas.toBlob(async (blob) => {
                    if (blob) {
                      try {
                        const formData = new FormData();
                        formData.append('frame_number', framesProcessed.toString());
                        formData.append('image_data', blob, `frame_${framesProcessed}.jpg`);
                        formData.append('timestamp', frameTime.toString());
                        formData.append('user_uuid', userUuid); // Use the fetched user UUID
                        if (userEmail) {
                          formData.append('user_email', userEmail); // Also add email if available
                        }
                        
                        const response = await fetch("http://localhost:8000/test", {
                          method: "POST",
                          body: formData,
                        });
                    
                        if (!response.ok) {
                          throw new Error(`Error processing frame: ${response.statusText}`);
                        }
                    
                        const result = await response.json();
                        console.log("Server response:", result);
                    
                        // Handle fire detection or other responses here...
                      } catch (error) {
                        console.error("Error sending frame to backend:", error);
                      }
                    }
                  }, 'image/jpeg', 0.8);
                }
                
                setTimeout(processFrames, 10);
              } catch (error) {
                console.error("Error processing frame:", error);
                processingRef.current = false;
                URL.revokeObjectURL(videoURL);
                reject(error);
              }
            };
            
            processFrames();
          };
        };
        
        video.onerror = () => {
          URL.revokeObjectURL(videoURL);
          processingRef.current = false;
          reject(new Error("Error loading video"));
        };
      } catch (error) {
        processingRef.current = false;
        reject(error);
      }
    });
  };

  const handleProcess = async () => {
    if (!file) {
      toast({
        title: "No file selected",
        description: "Please upload a video file first",
        variant: "destructive"
      });
      return;
    }

    if (!userUuid) {
      toast({
        title: "Authentication Required",
        description: "Please log in to process videos",
        variant: "destructive"
      });
      return;
    }

    setIsProcessing(true);
    setProcessProgress(0);
    
    try {
      await processVideo(file);
      setIsProcessing(false);
    } catch (error) {
      console.error("Error processing video:", error);
      setIsProcessing(false);
      processingRef.current = false;
      toast({
        title: "Processing Error",
        description: `Failed to process video: ${error instanceof Error ? error.message : "Unknown error"}`,
        variant: "destructive"
      });
    }
  };

  return (
    <div className="min-h-screen py-12 px-4 bg-gradient-to-b from-black to-red-950/30">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-r from-red-500 to-red-700 bg-clip-text text-transparent">
            Video Frame Processor
          </h1>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Upload a video to process its frames. You'll receive notifications every 100 frames.
          </p>
          {userEmail && (
            <p className="text-sm text-muted-foreground mt-2">
              Logged in as: {userEmail}
            </p>
          )}
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="border border-red-500/20 bg-black/40 shadow-lg shadow-red-500/5">
            <CardHeader>
              <CardTitle>Video Upload</CardTitle>
              <CardDescription>
                Upload a video file to begin processing
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div 
                className={`border-2 border-dashed rounded-lg p-6 text-center transition-all ${
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
                      onClick={() => {
                        setFile(null);
                      }}
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
                <div className="bg-black/60 rounded-lg p-4 border border-red-500/20">
                  <h3 className="text-lg font-medium mb-2">File Information</h3>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <p className="text-sm text-muted-foreground">File Name</p>
                      <p className="font-medium truncate">{file.name}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">File Size</p>
                      <p className="font-medium">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                    </div>
                  </div>
                </div>
              )}

              {isProcessing && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm mb-1">
                    <span>Processing frames</span>
                    <span>{processedFrames} / {totalFrames}</span>
                  </div>
                  <Progress value={processProgress} className="h-2 bg-red-950/30" />
                  <p className="text-xs text-muted-foreground text-center mt-1">
                    Processing video frames...
                  </p>
                </div>
              )}

              <Button 
                onClick={handleProcess}
                disabled={!file || isProcessing || !userUuid}
                className="w-full bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 shadow-lg shadow-red-500/20"
              >
                {isProcessing ? "Processing..." : "Process Video"}
              </Button>
            </CardContent>
          </Card>

          <Card className="border border-red-500/20 bg-black/40 shadow-lg shadow-red-500/5 overflow-hidden">
            <CardHeader className="pb-2">
              <CardTitle>Video Preview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="aspect-video bg-black/60 rounded-md overflow-hidden flex items-center justify-center">
                <video 
                  ref={videoRef} 
                  className="max-w-full max-h-full" 
                  controls={!isProcessing}
                />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Hidden canvas element - required for processing but not displayed */}
        <canvas ref={canvasRef} className="hidden" />
      </div>
    </div>
  );
}