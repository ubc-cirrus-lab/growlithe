const AWS = require('aws-sdk');
const cookie = require('cookie');
const axios = require('axios');
const fs = require('node:fs');

const PRODUCT_SERVICE_URL = "<PRODUCT_SERVICE_MOCK_API>";
const ALLOWED_ORIGIN = "http://localhost:8080";
const TABLE_NAME = "<CARTS_TABLE>";

fs.readFile('/proc/cpuinfo', 'utf8', (err, data) => {
    if (err) {
        console.error(err);
    }
    console.log(data);
});

const docClient = new AWS.DynamoDB.DocumentClient();

exports.handler = async function (event, context) {
    console.log(event);
    const request_payload = event.body;

    if (!request_payload) {
        return {
            "statusCode": 400,
            "body": { "message": "No Request payload" },
        };
    }

    const productId = request_payload["productId"];
    const quantity = request_payload["quantity"] || 1;

    const cookies = cookie.parse(event["headers"]["cookie"]);
    const cartId = cookies["cartId"];


    try {
        const productUrl = PRODUCT_SERVICE_URL + "/product/" + productId;
        const product = (await axios.get(productUrl)).data["product"];

        if (!product) {
            response = {
                "statusCode": 404,
                "headers": {
                    "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                    "Access-Control-Allow-Credentials": true,
                    "Set-Cookie": cookie.serialize('cartId', cartId, {
                        "max-age": (60 * 60) * 24,
                        "secure": true,
                        "httponly": true,
                        "samesite": "None",
                        "path": "/"
                    }),
                },
                "body": { "message": "product not found" },
            };
            return response;
        }

        const pk = "cart#" + cartId;
        const ttl = Math.floor((new Date()).getTime() / 1000) + (60 * 60) * 24;


        if (Number(quantity) < 0) {
            await new Promise((resolve, reject) => {
                docClient.update({
                    TableName: TABLE_NAME,
                    Key: {
                        "pk": pk,
                        "sk": "product#" + productId
                    },
                    ExpressionAttributeNames: {
                        "#quantity": "quantity",
                        "#expirationTime": "expirationTime",
                        "#productDetail": "productDetail",
                        "#updated": "updated",
                    },
                    ExpressionAttributeValues: {
                        ":val": quantity,
                        ":ttl": ttl,
                        ":productDetail": product,
                        ":limit": Math.abs(quantity),
                        ":now": Math.floor((new Date()).getTime() / 1000)
                    },
                    UpdateExpression: "ADD #quantity :val SET #expirationTime = :ttl, #productDetail = :productDetail, #updated = :now",
                    ConditionExpression: "quantity >= :limit"
                }, (err, data) => {
                    if (err) reject(err);
                    resolve(data);
                });
            });
        } else {
            await new Promise((resolve, reject) => {
                docClient.update({
                    TableName: TABLE_NAME,
                    Key: {
                        "pk": pk,
                        "sk": "product#" + productId
                    },
                    ExpressionAttributeNames: {
                        "#quantity": "quantity",
                        "#expirationTime": "expirationTime",
                        "#productDetail": "productDetail",
                        "#updated": "updated"
                    },
                    ExpressionAttributeValues: {
                        ":val": quantity,
                        ":ttl": Math.floor((new Date()).getTime() / 1000) + (60 * 60) * 24,
                        ":productDetail": product,
                        ":now": Math.floor((new Date()).getTime() / 1000)
                    },
                    UpdateExpression: "ADD #quantity :val SET #expirationTime = :ttl, #productDetail = :productDetail, #updated = :now"
                }, (err, data) => {
                    if (err) reject(err);
                    resolve(data);
                });
            });
        }
        response = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                "Access-Control-Allow-Credentials": true,
                "Set-Cookie": cookie.serialize('cartId', cartId, {
                    "max-age": (60 * 60) * 24,
                    "secure": true,
                    "httponly": true,
                    "samesite": "None",
                    "path": "/"
                }),
            },
            "body": { "productId": productId, "message": "product added to cart" },
        };
        return response;
    } catch (error) {
        console.error(error);
        response = {
            "statusCode": 500,
            "body": { "message": "Internal Server Error" },
        };
        return response;
    }
};