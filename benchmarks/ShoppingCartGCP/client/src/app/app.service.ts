import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Auth, signInWithEmailAndPassword } from '@angular/fire/auth';
import { firstValueFrom } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AppService {

  constructor() { }

  http = inject(HttpClient);
  auth = inject(Auth);

  async start() {
    const token = await this.login();
    await this.addToShoppingCart(token);
    await this.checkoutShoppingCart(token);
  }

  async login(): Promise<string> {
    const user = await signInWithEmailAndPassword(this.auth, 'test@test.com', 'tester');
    const token = await user.user.getIdToken();
    return token;
  }

  async addToShoppingCart(token: string) {
    return await firstValueFrom(
      this.http.post(
        'https://us-central1-data-terminus-393416.cloudfunctions.net/add-to-cart-function?authtoken=' + token,
        {
          productId: "4c1fadaa-213a-4ea8-aa32-58c217604e3c",
          quantity: 10
        },
        {
          withCredentials: true,
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )
    );
  }

  async checkoutShoppingCart(token: string) {
    console.log('checkoutShoppingCart');
    return await firstValueFrom(
      this.http.post(
      'https://us-central1-data-terminus-393416.cloudfunctions.net/checkout-cart-function?authtoken=' + token,
      {},
      {
        withCredentials: true,
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    )
  );
  }
}
