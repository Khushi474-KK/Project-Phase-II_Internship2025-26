import { initializeApp } from 'firebase/app';
import { 
  getAuth, 
  GoogleAuthProvider, 
  signInWithPopup, 
  signOut,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  fetchSignInMethodsForEmail,
  linkWithPopup,
  linkWithCredential,
  EmailAuthProvider,
  updateProfile,
  sendEmailVerification
} from 'firebase/auth';

const firebaseConfig = {
  apiKey: "AIzaSyA3Z7VjVSIqmn7CvhQ06ByfAYzzMR34eEk",
  authDomain: "myreactauthapp-14dfe.firebaseapp.com",
  projectId: "myreactauthapp-14dfe",
  storageBucket: "myreactauthapp-14dfe.firebasestorage.app",
  messagingSenderId: "121668604183",
  appId: "1:121668604183:web:e111ec19ccdb29e4eda752"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

// Check if user has password authentication linked
export const hasPasswordAuth = (user) => {
  if (!user) return false;
  const providers = user.providerData.map(p => p.providerId);
  return providers.includes('password');
};

// Check if user needs profile completion
// Only Google users who haven't set up password need profile completion
export const needsProfileCompletion = (user) => {
  if (!user) return false;
  
  // Get provider IDs
  const providers = user.providerData.map(p => p.providerId);
  
  // User needs completion ONLY if:
  // 1. They signed in with Google (has google.com provider)
  // 2. AND they don't have password auth yet
  const hasGoogle = providers.includes('google.com');
  const hasPassword = providers.includes('password');
  
  // Only show profile completion for Google-only users
  return hasGoogle && !hasPassword;
};

// Email/Password Registration
export const registerWithEmail = async (email, password, username) => {
  try {
    console.log('Attempting to register with email:', email);
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    console.log('User created successfully:', userCredential.user.uid);
    
    // Update profile with username
    if (username) {
      await updateProfile(userCredential.user, {
        displayName: username
      });
      console.log('Username updated:', username);
    }
    
    // Send email verification
    try {
      await sendEmailVerification(userCredential.user);
      console.log('Verification email sent to:', email);
    } catch (verifyError) {
      console.warn('Could not send verification email:', verifyError);
      // Don't fail registration if email verification fails
    }
    
    return userCredential.user;
  } catch (error) {
    console.error('Error registering with email:', error.code, error.message);
    
    if (error.code === 'auth/operation-not-allowed') {
      throw new Error('Email/Password authentication is not enabled. Please contact the administrator.');
    } else if (error.code === 'auth/email-already-in-use') {
      throw new Error('This email is already registered. Please sign in instead.');
    } else if (error.code === 'auth/invalid-email') {
      throw new Error('Invalid email address.');
    } else if (error.code === 'auth/weak-password') {
      throw new Error('Password is too weak. Please use at least 6 characters.');
    }
    
    throw error;
  }
};

// Email/Password Login
export const loginWithEmail = async (email, password) => {
  try {
    console.log('Attempting to login with email:', email);
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    console.log('Login successful:', userCredential.user.uid);
    return userCredential.user;
  } catch (error) {
    console.error('Error logging in with email:', error.code, error.message);
    
    if (error.code === 'auth/operation-not-allowed') {
      throw new Error('Email/Password authentication is not enabled.');
    } else if (error.code === 'auth/user-not-found') {
      throw new Error('No account found with this email.');
    } else if (error.code === 'auth/wrong-password') {
      throw new Error('Incorrect password.');
    } else if (error.code === 'auth/invalid-email') {
      throw new Error('Invalid email address.');
    }
    
    throw error;
  }
};

// Google Sign-In with Provider Linking
export const signInWithGoogle = async () => {
  try {
    console.log('Attempting Google sign-in...');
    const result = await signInWithPopup(auth, googleProvider);
    console.log('Google sign-in successful:', result.user.uid);
    return { user: result.user, needsLinking: false };
  } catch (error) {
    console.error('Error signing in with Google:', error.code, error.message);
    
    if (error.code === 'auth/operation-not-allowed') {
      throw new Error('Google authentication is not enabled. Please contact the administrator.');
    }
    
    // Handle account exists with different credential
    if (error.code === 'auth/account-exists-with-different-credential') {
      const email = error.customData?.email;
      console.log('Account exists with different credential for email:', email);
      
      if (email) {
        try {
          // Fetch existing sign-in methods
          const methods = await fetchSignInMethodsForEmail(auth, email);
          console.log('Existing sign-in methods:', methods);
          
          // Store the pending credential for later linking
          const pendingCredential = error.credential;
          
          return {
            error: 'account-exists',
            email: email,
            existingMethods: methods,
            pendingCredential: pendingCredential,
            message: `An account already exists with ${email}. Please sign in with your password first, then we'll link your Google account.`
          };
        } catch (fetchError) {
          console.error('Error fetching sign-in methods:', fetchError);
          throw new Error('Unable to verify existing account.');
        }
      }
    }
    
    if (error.code === 'auth/popup-closed-by-user') {
      throw new Error('Sign-in popup was closed.');
    }
    
    throw error;
  }
};

// Complete Profile for Google Users (add password and username)
export const completeProfile = async (username, password) => {
  try {
    const user = auth.currentUser;
    if (!user) {
      throw new Error('No user is currently signed in.');
    }
    
    console.log('Completing profile for user:', user.uid);
    
    // Update display name if provided
    if (username && username !== user.displayName) {
      await updateProfile(user, {
        displayName: username
      });
      console.log('Username updated:', username);
    }
    
    // Link password authentication if provided
    if (password) {
      const credential = EmailAuthProvider.credential(user.email, password);
      await linkWithCredential(user, credential);
      console.log('Password authentication linked successfully');
    }
    
    // Reload user to get updated provider data
    await user.reload();
    return auth.currentUser;
  } catch (error) {
    console.error('Error completing profile:', error.code, error.message);
    
    if (error.code === 'auth/provider-already-linked') {
      throw new Error('Password authentication is already set up for this account.');
    } else if (error.code === 'auth/weak-password') {
      throw new Error('Password is too weak. Please use at least 6 characters.');
    } else if (error.code === 'auth/requires-recent-login') {
      throw new Error('Please sign out and sign in again before completing your profile.');
    }
    
    throw error;
  }
};

// Link Google Account to Existing Email/Password Account
export const linkGoogleAccount = async () => {
  try {
    if (!auth.currentUser) {
      throw new Error('No user is currently signed in.');
    }
    
    console.log('Attempting to link Google account for user:', auth.currentUser.uid);
    const result = await linkWithPopup(auth.currentUser, googleProvider);
    console.log('Google account linked successfully:', result.user.uid);
    
    // Log provider info
    const providers = result.user.providerData.map(p => p.providerId);
    console.log('User now has providers:', providers);
    
    return result.user;
  } catch (error) {
    console.error('Error linking Google account:', error.code, error.message);
    
    if (error.code === 'auth/credential-already-in-use') {
      throw new Error('This Google account is already linked to another user.');
    } else if (error.code === 'auth/provider-already-linked') {
      throw new Error('Google account is already linked to this user.');
    } else if (error.code === 'auth/requires-recent-login') {
      throw new Error('Please sign out and sign in again before linking your Google account.');
    }
    
    throw error;
  }
};

// Link Google provider with pending credential (after password login)
export const linkGoogleWithCredential = async (pendingCredential) => {
  try {
    if (!auth.currentUser) {
      throw new Error('No user is currently signed in.');
    }
    
    console.log('Linking Google provider with pending credential...');
    const result = await linkWithCredential(auth.currentUser, pendingCredential);
    console.log('Google provider linked successfully:', result.user.uid);
    
    // Log provider info
    const providers = result.user.providerData.map(p => p.providerId);
    console.log('User now has providers:', providers);
    
    return result.user;
  } catch (error) {
    console.error('Error linking with credential:', error.code, error.message);
    
    if (error.code === 'auth/credential-already-in-use') {
      throw new Error('This Google account is already linked to another user.');
    } else if (error.code === 'auth/provider-already-linked') {
      // Already linked, this is actually success
      console.log('Provider already linked, continuing...');
      return auth.currentUser;
    }
    
    throw error;
  }
};

// Sign Out
export const signOutUser = async () => {
  try {
    console.log('Signing out user...');
    await signOut(auth);
    console.log('Sign out successful');
  } catch (error) {
    console.error('Error signing out:', error);
    throw error;
  }
};

export { auth };
