import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Dashboard() {
    // Input data
    const [imageUrl, setImageUrl] = useState('');
    const [description, setDescription] = useState('');

    const [displayImageUrl, setDisplayImageUrl] = useState('');

    // Output data
    const [imageData, setImageData] = useState([]);

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


    const uploadPicture = () => {
        if (!imageUrl) {
            console.error('No image URL provided');
            return;
        }

        // Set image url to backend
        setDisplayImageUrl(imageUrl);
        console.log('Image URL set:', imageUrl);

        axios.post('http://localhost:5001/api/match-image', { url: imageUrl, n: 3 })
            .then(response => {
                console.log('Image URL sent successfully:', response.data);
                setImageData(response.data);
            })
            .catch(error => {
                console.error('Error sending image URL:', error);
            });
    };

    const uploadDescription = () => {
        if (!description) {
            console.error('No description provided');
            return;
        }

        console.log('Description set:', description);

        // Send description to the backend
        axios.post('http://localhost:5001/api/match-prompt', { prompt: description, n: 3 })
            .then(response => {
                console.log('Description sent successfully:', response.data);
                setImageData(response.data);
            })
            .catch(error => {
                console.error('Error sending description:', error);
            });
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
            <button onClick={uploadPicture}>Upload Picture</button>
            {displayImageUrl && (
                <img
                    src={displayImageUrl}
                    alt="Display"
                    style={{ maxWidth: '500px', maxHeight: '500px' }}
                />
            )}
            <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe the item you are looking for"
            />
            <button onClick={uploadDescription}>Send Description</button>
            <div style={{ display: 'flex', justifyContent: 'space-around', marginTop: '20px' }}>
                {imageData.map((img, index) => (
                    <div key={index} style={{ textAlign: 'center' }}>
                        <img src={img.url} alt={`Similar Image ${index + 1}`} style={{ maxWidth: '300px', maxHeight: '300px' }} />
                        <p>Similarity Score: {img.score}</p>
                    </div>
                ))}
            </div>

        </div>
    );
}

export default Dashboard;
