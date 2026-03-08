// Firebase configuration - Web SDK
import { initializeApp } from "firebase/app";
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut } from "firebase/auth";
import { getFirestore, collection, addDoc, query, where, getDocs, updateDoc, doc } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyBfqNip6xbHDhKUIr49Oq7mTjieLfQ77SM",
  authDomain: "camp-prjct-tracker.firebaseapp.com",
  projectId: "camp-prjct-tracker",
  storageBucket: "camp-prjct-tracker.appspot.com",
  messagingSenderId: "655573218229",
  appId: "1:655573218229:web:71a92159201ce1f1cd9ffc",
  measurementId: "G-1Z2B5PSYJR"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

// Export authentication functions
export { auth, db, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut };
export { collection, addDoc, query, where, getDocs, updateDoc, doc };
