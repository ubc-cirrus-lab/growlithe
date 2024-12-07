# Benchmark 3 (GCP) - Shopping Cart

## Deployment

1. Ensure that [dotenvx](https://dotenvx.com/) and [Terraform](https://www.terraform.io/) are installed on your computer.
2. Create a Service Account in your GCP project.
3. Download the service account key in JSON.
4. Put the service account key in the `terraform/` folder.
5. Run `deploy.sh` in the `terraform/` directory.
6. Run the `terraform/set-user-region/setuserregion.js` script after install its necessary dependencies specified in `package.json`.

## Testing

0. CD to the `client/` directory
1. Run `npm install`.
2. Run `npx ng serve`.
3. Open the link printed out in the console in your browser press the "Login and Add and Checkout" to test the workflow.