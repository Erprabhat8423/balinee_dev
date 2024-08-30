importScripts('https://www.gstatic.com/firebasejs/8.2.4/firebase.js');
importScripts('https://www.gstatic.com/firebasejs/8.2.4/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/8.2.4/firebase-messaging.js');

var firebaseConfig = {
    apiKey: "AIzaSyCubxF4N5V_w2c9g9obVj_U7YBzhnDD-JU",
    authDomain: "sansthaa-20b83.firebaseapp.com",
    projectId: "sansthaa-20b83",
    storageBucket: "sansthaa-20b83.appspot.com",
    messagingSenderId: "281121207327",
    appId: "1:281121207327:web:46618196c8b1a94048112a",
    measurementId: "G-7DMY4ZH0ER"
};
// Initialize Firebase
firebase.initializeApp(firebaseConfig);


var messaging = firebase.messaging();


messaging.onBackgroundMessage((payload) => {
    // console.log('[firebase-messaging-sw.js] Received background message ', payload);
    // // Customize notification here
    // const notificationTitle = 'Background Message Title';
    // const notificationOptions = {
    //   body: 'Background Message body.',
    //   icon: '/firebase-logo.png'
    // };
  
    // self.registration.showNotification(notificationTitle,
    //   notificationOptions);
  });
  

  