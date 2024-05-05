import React, { useState, useEffect } from 'react';
import axios from 'axios';

import Slider from 'react-slick';
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";



function Dashboard() {
    // Input data
    const [imageUrl, setImageUrl] = useState('');
    const [description, setDescription] = useState('');

    const [displayImageUrl, setDisplayImageUrl] = useState('');

    // Output data
    const [imageData, setImageData] = useState([]);

    const [logs, setLogs] = useState([]);

    const settings = {  // Carousel settings
        dots: true,
        infinite: true,
        speed: 500,
        slidesToShow: 1,
        slidesToScroll: 1
    };


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
        console.log('Image URL set:', imageUrl);

        axios.post('http://localhost:5001/api/match-image', { url: imageUrl, n: 6 })
            .then(response => {
                console.log('Image URL sent successfully:', response.data);
                setImageData(response.data);
                console.log(imageData);


            })
            .catch(error => {
                console.error('Error sending image URL:', error);
            }).finally(() => {
                setDisplayImageUrl(imageUrl);
            });
    };

    const uploadBoth = () => {
        if (!description) {
            console.error('No description provided');
            return;
        }

        if (!imageUrl) {
            console.error('No image URL provided');
            return;
        }

        console.log('Description set:', description);
        console.log('Image URL set:', imageUrl);


        // Send description to the backend
        axios.post('http://localhost:5001/api/match-both', { prompt: description, url: imageUrl, n: 6 })
            .then(response => {
                console.log('Prompt and Url sent successfully:', response.data);
                setImageData(response.data);
            })
            .catch(error => {
                console.error('Error sending image and url:', error);
            });
    };

    const uploadDescription = () => {
        if (!description) {
            console.error('No description provided');
            return;
        }

        console.log('Description set:', description);

        // Send description to the backend
        axios.post('http://localhost:5001/api/match-prompt', { prompt: description, n: 6 })
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
            <header className="fixed-header">
                <h2>INDITEX</h2>
                <h1>Fashion-AId</h1>
            </header>

            <div className="content-container">
                <p>Welcome to INDITEX Fashion-AId, Your Personal AI-based Fashion Assistant!</p>
                <p>Discover your next favorite clothing piece with just a click! Upload a picture or enter a description, and let our advanced AI technology instantly recommend clothing that matches your style and preferences. Whether you're refreshing your wardrobe or searching for that perfect piece, our intuitive system makes finding fashion effortless and fun. Get ready to elevate your style with personalized recommendations tailored just for you!</p>

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
                        style={{ maxWidth: '400px', maxHeight: '400px' }}
                    />
                )}
                <input
                    type="text"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Describe the item you are looking for"
                />
                <button onClick={uploadDescription}>Upload Prompt</button>
                <button onClick={uploadBoth}>Upload Picture with Prompt</button>

                <div style={{ display: 'flex', flexDirection: 'row', flexWrap: 'wrap', maxWidth: '100%', overflowX: 'auto' }}>
                    {imageData.map((img, index) => (
                        <div key={index} style={{ flex: '1 0 auto', maxWidth: '300px', textAlign: 'center', margin: '20px' }}>
                            <Slider {...settings}>
                                {img.url.map((url, urlIndex) => (
                                    <div key={urlIndex}>
                                        <img src={url} alt={`Image ${index + 1}-${urlIndex}`} style={{ width: '100%', height: 'auto' }} />
                                    </div>
                                ))}
                            </Slider>
                            <p>{img.document}</p>
                            <p>Similarity Score: {((1 - img.score) * 100).toFixed(2)} % </p>
                        </div>
                    ))}
                </div>

            </div>

        </div>
    );
}

export default Dashboard;
