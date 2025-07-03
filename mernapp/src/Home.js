import React, { useState, useRef } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';
import './Home.css';

function IDValidatorApp() {
  const [file, setFile] = useState(null);
  const [userId, setUserId] = useState("22-733-043");
  const [response, setResponse] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const webcamRef = useRef(null);
  const [usingWebcam, setUsingWebcam] = useState(false);

  const toBase64 = (file) => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result.split(',')[1]);
    reader.onerror = error => reject(error);
  });

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setResponse(null);
      setImagePreview(URL.createObjectURL(selectedFile));
      setUsingWebcam(false);
    }
  };

const captureImage = () => {
  const screenshot = webcamRef.current.getScreenshot();
  if (screenshot) {
    fetch(screenshot)
      .then(res => res.blob())
      .then(blob => {
        const fileFromWebcam = new File([blob], "webcam-capture.jpg", { type: "image/jpeg" });
        setFile(fileFromWebcam);
        setImagePreview(screenshot);
        setUsingWebcam(false); // <- THIS TURNS OFF THE WEBCAM
        setResponse(null);
      });
  }
};


  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return alert("Please upload an ID card or take a photo");

    try {
      const base64Image = await toBase64(file);
      const payload = {
        user_id: userId,
        image_base64: base64Image
      };

      const res = await axios.post("http://localhost:8000/validate-id", payload);
      setResponse(res.data);
    } catch (err) {
      console.error(err);
      alert("Error uploading image");
    }
  };

  const styles = {
    container: {
      width: '90vw',
      maxWidth: '700px',
      margin: '40px auto',
      padding: '20px 30px',
      border: '1px solid #ddd',
      borderRadius: '12px',
      backgroundColor: '#fafafa',
      boxShadow: '0 6px 15px rgba(0,0,0,0.1)',
      fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
      color: '#333',
      minHeight: '80vh',
      boxSizing: 'border-box',
    },
    heading: {
      textAlign: 'center',
      marginBottom: '25px',
      color: '#1a73e8',
      fontWeight: '700',
      fontSize: '2.8rem',
      letterSpacing: '1.5px',
    },
    uploadLabel: {
      display: 'inline-block',
      padding: '14px 30px',
      backgroundColor: '#1a73e8',
      color: '#fff',
      borderRadius: '10px',
      cursor: 'pointer',
      fontWeight: '600',
      marginBottom: '15px',
      userSelect: 'none',
      transition: 'background-color 0.3s ease',
      fontSize: '1.15rem',
    },
    fileName: {
      marginTop: '10px',
      fontStyle: 'italic',
      color: '#555',
      fontSize: '1.1rem',
    },
    validateBtn: {
      display: 'block',
      width: '100%',
      padding: '15px 0',
      backgroundColor: '#0d47a1',
      color: '#fff',
      border: 'none',
      borderRadius: '10px',
      fontSize: '1.25rem',
      fontWeight: '700',
      cursor: 'pointer',
      marginTop: '20px',
      transition: 'background-color 0.3s ease',
    },
    previewContainer: {
      marginTop: '30px',
      textAlign: 'center',
    },
    previewImage: {
      maxWidth: '100%',
      maxHeight: '400px',
      borderRadius: '10px',
      border: '1px solid #ccc',
      boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
    },
    previewHeading: {
      marginBottom: '15px',
      color: '#1a73e8',
      fontWeight: '700',
      fontSize: '1.8rem',
    },
    webcamContainer: {
      margin: '20px 0',
      textAlign: 'center',
    },
    captureBtn: {
      marginTop: '10px',
      padding: '12px 25px',
      backgroundColor: '#1a73e8',
      color: '#fff',
      border: 'none',
      borderRadius: '10px',
      fontSize: '1rem',
      fontWeight: '600',
      cursor: 'pointer',
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>College ID Card Validator</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ textAlign: 'center', marginBottom: '20px' }}>
  <button
    type="button"
    style={styles.uploadLabel}
    onClick={() => {
      document.getElementById('fileInput').click();
    }}
    onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#0d47a1'}
    onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#1a73e8'}
  >
    Upload ID
  </button>
  <input
    id="fileInput"
    type="file"
    accept="image/*"
    onChange={handleFileChange}
    style={{ display: 'none' }}
  />

  <button
    type="button"
    style={{ ...styles.uploadLabel, backgroundColor: '#34a853', marginLeft: '10px' }}
    onClick={() => {
      setUsingWebcam(true);
      setFile(null);
      setImagePreview(null);
      setResponse(null);
    }}
    onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#1b7e38'}
    onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#34a853'}
  >
    Take Picture Using Camera
  </button>
</div>

{usingWebcam && (
  <div style={styles.webcamContainer}>
    <Webcam
      audio={false}
      ref={webcamRef}
      screenshotFormat="image/jpeg"
      width="100%"
      style={{ borderRadius: '10px' }}
    />
    <button type="button" onClick={captureImage} style={styles.captureBtn}>
      Capture from Webcam
    </button>
  </div>
)}


        {file && <div style={styles.fileName}>Selected File: {file.name}</div>}

        <button
          type="submit"
          style={styles.validateBtn}
          onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#08306b'}
          onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#0d47a1'}
        >
          Validate ID
        </button>
      </form>

      {imagePreview && (
        <div style={styles.previewContainer}>
          <h3 style={styles.previewHeading}>Image Preview:</h3>
          <img
            src={imagePreview}
            alt="ID Preview"
            style={styles.previewImage}
          />
        </div>
      )}

      {response && (
        <div className="result-box" style={{ marginTop: '40px', padding: '20px', border: '1px solid #ccc', borderRadius: '10px', background: '#f8f9fa' }}>
          <h3 style={{ color: '#0d47a1' }}>Validation Result</h3>
          <p><strong>Status:</strong> {response.status}</p>
          <p><strong>Message:</strong> {response.message}</p>
          <p><strong>User ID:</strong> {response.user_id}</p>

          <h4 style={{ marginTop: '20px', color: '#1a73e8' }}>Validation Details:</h4>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <tbody>
  <tr><td><strong>User ID Match</strong></td><td>{String(response.text_validation.user_id_match)}</td></tr>
  <tr><td><strong>Extracted Name</strong></td><td>{String(response.text_validation.name_extracted)}</td></tr>
  <tr><td><strong>Roll Number</strong></td><td>{response.text_validation.roll_number ?? 'N/A'}</td></tr>
  <tr><td><strong>Branch</strong></td><td>{response.text_validation.branch ?? 'N/A'}</td></tr>
  <tr><td><strong>College Found</strong></td><td>{String(response.text_validation.college_found)}</td></tr>
  <tr><td><strong>Matched College</strong></td><td>{response.text_validation.matched_college ?? 'N/A'}</td></tr>
  <tr><td><strong>Face Photo Found</strong></td><td>{String(response.text_validation.face_photo_found)}</td></tr>
  <tr>
    <td><strong>OCR Confidence</strong></td>
    <td>
      {response.ocr_confidence !== undefined && response.ocr_confidence !== null
        ? response.ocr_confidence.toFixed(2)
        : 'N/A'}
    </td>
  </tr>
  <tr><td><strong>Image Classification</strong></td><td>{response.image_classification?.predicted_class ?? 'N/A'}</td></tr>
  <tr>
    <td><strong>Genuine Confidence</strong></td>
    <td>
      {response.image_classification?.genuine_confidence !== undefined && response.image_classification?.genuine_confidence !== null
        ? response.image_classification.genuine_confidence.toFixed(4)
        : 'N/A'}
    </td>
  </tr>
  <tr>
    <td><strong>Template Similarity Score</strong></td>
    <td>
      {response.image_classification?.template_similarity_score !== undefined &&
      response.image_classification?.template_similarity_score !== null
        ? response.image_classification.template_similarity_score.toFixed(4)
        : 'N/A'}
    </td>
  </tr>
  <tr>
    <td><strong>All Class Probabilities</strong></td>
    <td>
      {response.image_classification?.all_probabilities
        ? Object.entries(response.image_classification.all_probabilities).map(
            ([label, prob]) => `${label}: ${prob.toFixed(4)}`
          ).join(', ')
        : 'N/A'}
    </td>
  </tr>
  <tr><td><strong>Validation Score</strong></td>
    <td>
      {response.validation_score !== undefined && response.validation_score !== null
        ? response.validation_score.toFixed(4)
        : 'N/A'}
    </td>
  </tr>
  <tr><td><strong>Output Label</strong></td><td>{response.label ?? 'N/A'}</td></tr>
  <tr><td><strong>Action</strong></td><td>{response.action ?? 'N/A'}</td></tr>
  <tr><td><strong>Reason</strong></td><td>{response.reason ?? 'N/A'}</td></tr>
</tbody>

          </table>

          <h4 style={{ marginTop: '20px', color: '#1a73e8' }}>Extracted Text:</h4>
          <div style={{
            background: '#fff',
            padding: '15px',
            borderRadius: '8px',
            boxShadow: 'inset 0 0 5px rgba(0,0,0,0.1)',
            whiteSpace: 'pre-wrap',
            lineHeight: '1.5',
            fontFamily: 'monospace',
            color: '#444'
          }}>
            {response.extracted_text}
          </div>
        </div>
      )}
    </div>
  );
}

export default IDValidatorApp;
