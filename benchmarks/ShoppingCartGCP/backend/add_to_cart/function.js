const { Firestore, FieldValue } = require('@google-cloud/firestore');
const admin = require('firebase-admin');
const axios = require('axios');
const cookie = require('cookie');
const functions = require('@google-cloud/functions-framework');

// Initialize Firestore
admin.initializeApp();
const db = new Firestore({
    databaseId: 'carts-db'
});
const auth = admin.auth();


functions.http('addToCart', async (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', 'http://localhost:4200');
    const request_payload = req.body;

    const claims = await auth.verifyIdToken(req.query['authtoken']);
    
    if (!request_payload) {
        return res.send( "No Request payload" );
    }
    
    const productId = request_payload.productId; 
    const quantity = request_payload.quantity || 1;
    
    const cookies = cookie.parse(req.headers.authorization || '');
    const cartId = cookies.cartId || claims['uid'];
    
    const product = (await axios.get("https://n6sp477ne0.execute-api.us-west-1.amazonaws.com/Prod" + "/product/" + productId)).data["product"];

    if (!product) {
        res.setHeader('Set-Cookie', cookie.serialize('cartId', cartId, {
            maxAge: 60 * 60 * 24, // 1 day
            secure: true,
            httpOnly: true,
            sameSite: 'None',
            path: '/'
        }));
        return res.send("Product not found");
    }
    
        
    const pk = `cart#${cartId}`;
    const sk = `product#${productId}`;
    const ttl = Math.floor((new Date()).getTime() / 1000) + (60 * 60) * 24; // 1 day expiration
    
    const cartDoc = db.collection('carts').doc(`${pk}#${sk}`);
    
    if (Number(quantity) < 0) {
        await cartDoc.update({
            pk,
            sk,
            quantity: FieldValue.increment(quantity),
            productDetail: product,
            updated: Math.floor((new Date()).getTime() / 1000)
        });
    } else {
        await cartDoc.set({
            pk,
            sk,
            quantity: FieldValue.increment(quantity),
            expirationTime: ttl,
            productDetail: product,
            updated: Math.floor((new Date()).getTime() / 1000)
        }, { merge: true });
    }
    
    res.setHeader('Set-Cookie', cookie.serialize('cartId', cartId, {
        maxAge: 60 * 60 * 24, // 1 day
        secure: true,
        httpOnly: true,
        sameSite: 'None',
        path: '/'
    }));
    console.log('woot woot');
    return res.json({ productId, message: "product added to cart" });
});
