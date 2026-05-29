const firebaseConfig = {
  apiKey: "AIzaSyAOIMrsepVj9PLubDYAeUA-Qowse2GlTXI",
  authDomain: "sterlo-kids-banking.firebaseapp.com",
  databaseURL: "https://sterlo-kids-banking-default-rtdb.europe-west1.firebasedatabase.app",
  projectId: "sterlo-kids-banking",
  storageBucket: "sterlo-kids-banking.firebasestorage.app",
  messagingSenderId: "39217932124",
  appId: "1:39217932124:web:be09cd44487c4b904a8399"
};

firebase.initializeApp(firebaseConfig);

function login() {
  var userEmail = document.getElementById('email_field').value
  var userPass = document.getElementById('password_field').value

  firebase.auth().signInWithEmailAndPassword(userEmail, userPass)
    .then(() => {
      localStorage.setItem("allowedLogin", "true");
      window.location.href = "/dashboard";
    })
    .catch(function (error) {
      window.alert('Error : ' + error.message)
    })
}

function logout() {
  firebase.auth().signOut().then(() => {
    localStorage.setItem("allowedLogin", "false");
    window.location.href = "/";
  })
}

function goToMembers() {
  window.location.href = "/dashboard/members";
}

function goToDashboard() {
  window.location.href = "/dashboard";
}

function goToAllergies() {
  window.location.href = "/dashboard/allergies";
}

function goToAttendance() {
  window.location.href = "/dashboard/attendance";
}

function goToProjects() {
  window.location.href = "/dashboard/projects";
}