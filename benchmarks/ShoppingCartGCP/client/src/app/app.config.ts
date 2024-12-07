import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { initializeApp, provideFirebaseApp } from '@angular/fire/app';
import { getAuth, provideAuth } from '@angular/fire/auth';
import { provideHttpClient } from '@angular/common/http';

export const appConfig: ApplicationConfig = {
  providers: [provideZoneChangeDetection({ eventCoalescing: true }), provideRouter(routes), provideHttpClient(), provideFirebaseApp(() => initializeApp({ "projectId": "data-terminus-393416", "appId": "1:549434878864:web:2ae964531744224c112115", "storageBucket": "data-terminus-393416.appspot.com", "locationId": "us-central", "apiKey": "AIzaSyDgLPT6dPq917brkyccACec0LIvfH1APpU", "authDomain": "data-terminus-393416.firebaseapp.com", "messagingSenderId": "549434878864" } as any)), provideAuth(() => getAuth())]
};
