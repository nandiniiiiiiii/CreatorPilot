import React, { useState, ChangeEvent } from "react";
import axios from "axios";

const VideoComponent: React.FC = () => {
    const [videoFile, setVideoFile] = useState<File | null>(null);
    const [captions, setCaptions] = useState<string>("");
    const [loading, setLoading] = useState<boolean>(false);
    const [videoPath, setVideoPath] = useState("");
    const [captionsPath, setCaptionsPath] = useState("");
    const [processedVideo, setProcessedVideo] = useState("")

    const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setVideoFile(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!videoFile) {
            alert("Please upload a video first.");
            return;
        }

        const formData = new FormData();
        formData.append("file", videoFile);

        setLoading(true);
        setCaptions(""); // Clear old captions

        try {
            const response = await axios.post<{ captions: string }>(
                "http://127.0.0.1:5000/upload",
                formData,
                {
                    headers: { "Content-Type": "multipart/form-data" },
                }
            );
            setCaptions(response.data.captions);
        } catch (error: any) {
            const errorMessage =
                error.response?.data?.error || error.message || "Unknown error occurred.";
            alert(`Error uploading video: ${errorMessage}`);
        } finally {
            setLoading(false);
        }
    };

    const handleAddCaptions = async () => {
        setLoading(true);
        try {
            const response = await fetch("http://localhost:5000/add_captions", {
                method: "POST",
            });
    
            if (response.ok) {
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                setProcessedVideo(url);
            } else {
                const data = await response.json();
                alert(data.error);
            }
        } catch (error) {
            alert("Error adding captions.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
            <h1>CreatorPilot</h1>
            <h2>Video Caption Generator</h2>

            <input type="file" accept="video/*" onChange={handleFileChange} />
            <button
                onClick={handleUpload}
                style={{
                    marginLeft: "10px",
                }}
                disabled={loading}
            >
                {loading ? "Processing..." : "Upload"}
            </button>

            {captions && (
                <div style={{ marginTop: "20px" }}>
                    <h3>Generated Captions:</h3>
                    <p
                        style={{
                            background: "#f4f4f4",
                            padding: "10px",
                            borderRadius: "5px",
                        }}
                    >
                        {captions}
                    </p>
                    <button
                        onClick={handleAddCaptions}
                        style={{ marginTop: "10px" }}
                        disabled={loading}
                    >
                        {loading ? "Adding Captions..." : "Add Captions to Video"}
                    </button>
                </div>
            )}

            {processedVideo && (
                <div style={{ marginTop: "20px" }}>
                    <h3>Processed Video:</h3>
                    <video controls width="600">
                        <source src={processedVideo} type="video/mp4" />
                        Your browser does not support the video tag.    
                    </video>
                </div>
            )}
        </div>
    )
}

export default VideoComponent