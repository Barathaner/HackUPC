import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Dashboard() {
    const [imageUrl, setImageUrl] = useState('');
    const [displayImageUrl, setDisplayImageUrl] = useState('');
    const [logs, setLogs] = useState([]);

    // Function to capture console logs
    useEffect(() => {
        const originalLog = console.log;
        console.log = (...args) => {
            setLogs(prevLogs => [...prevLogs, ...args.map(arg => JSON.stringify(arg))]);
            originalLog(...args);
        };
        return () => console.log = originalLog;
    }, []);

    const handleSetPicture = () => {
        setDisplayImageUrl(imageUrl);
        console.log('Image URL set:', imageUrl);
    };

    const sendPictureToBackend = () => {
        // Make sure the URL points to your Flask backend
        axios.post('http://localhost:5001/api/send-image', { url: displayImageUrl })
            .then(response => console.log('Image URL sent successfully:', response.data))
            .catch(error => console.error('Error sending image URL:', error));
    };


    return (
        <div>
            <h1>Dashboard</h1>
            <input
                type="text"
                value={imageUrl}
                onChange={(e) => setImageUrl(e.target.value)}
                placeholder="Enter image URL here"
            />
            <button onClick={handleSetPicture}>Set Picture</button>
            <img
                src={displayImageUrl}
                alt="Display"
                style={{ maxWidth: '500px', maxHeight: '500px' }}  // Maintain aspect ratio with max constraints
            />
            <button onClick={sendPictureToBackend}>Send Picture to Backend</button>
            <div className="console-log">
                <h2>Console Logs</h2>
                <div>{logs.map((log, index) => <div key={index}>{log}</div>)}</div>
            </div>
        </div>
    );
}

export default Dashboard;
