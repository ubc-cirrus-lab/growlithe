#!/usr/bin/env node

const admin = require('firebase-admin');

admin.initializeApp({
    credential: admin.credential.cert(require('../serviceAccountKey.json')),
});

async function main() {
    const user = await admin.auth().createUser({ displayName: 'Test User', email: 'test@test.test', password: 'tester' });
    await admin.auth().setCustomUserClaims(user.uid, { region: 'CA' });
    console.log(user.uid);
}

main().then(() => console.log('Region has been set!'));
