// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAOIMrsepVj9PLubDYAeUA-Qowse2GlTXI",
  authDomain: "sterlo-kids-banking.firebaseapp.com",
  databaseURL: "https://sterlo-kids-banking-default-rtdb.europe-west1.firebasedatabase.app",
  projectId: "sterlo-kids-banking",
  storageBucket: "sterlo-kids-banking.firebasestorage.app",
  messagingSenderId: "39217932124",
  appId: "1:39217932124:web:be09cd44487c4b904a8399"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);