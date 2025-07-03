import React from 'react';
import { Link } from "react-router-dom";
import Footer from '../components/Footer.js';
import Navbar from '../components/Navbar.js';
import Card from './Card.js';
import Carrousal from './Carrousal.js';
export default function Home() {
  return (
    <div>
      <Navbar />
      <Carrousal></Carrousal>
      <div>
        <Card></Card>
      </div>
      <Footer />
    </div>
  );
}
