import React from 'react';

export default function Carrousal() {
  return (
    <div>
      <div id="carouselExampleControls" className="carousel slide" data-bs-ride="carousel">
        <div className="carousel-inner">
          <div className="carousel-item active">
            <img className="d-block w-100" src="https://tse4.mm.bing.net/th?id=OIP.9vOj25uyE-Aj7RUw1WM2xgHaE8&pid=Api&P=0&h=180" alt="First slide" />
          </div>
          <div className="carousel-item">
            <img className="d-block w-100" src="https://tse3.mm.bing.net/th?id=OIP.H8fX5eBqf9HU3EROcTUbzQHaEo&pid=Api&P=0&h=180" alt="Second slide" />
          </div>
          <div className="carousel-item">
            <img className="d-block w-100" src="https://tse4.mm.bing.net/th?id=OIP.9vOj25uyE-Aj7RUw1WM2xgHaE8&pid=Api&P=0&h=180" alt="Third slide" />
          </div>
        </div>
        <button className="carousel-control-prev" type="button" data-bs-target="#carouselExampleControls" data-bs-slide="prev">
          <span className="carousel-control-prev-icon" aria-hidden="true"></span>
          <span className="visually-hidden">Previous</span>
        </button>
        <button className="carousel-control-next" type="button" data-bs-target="#carouselExampleControls" data-bs-slide="next">
          <span className="carousel-control-next-icon" aria-hidden="true"></span>
          <span className="visually-hidden">Next</span>
        </button>
      </div>
    </div>
  );
}
