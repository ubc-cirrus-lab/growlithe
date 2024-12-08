rm -f add_to_cart.zip 
rm -f checkout_cart.zip 
zip -r -j add_to_cart.zip ../backend/add_to_cart/**/* 
zip -r -j checkout_cart.zip ../backend/checkout_cart/**/* 
bunx @dotenvx/dotenvx run -- terraform apply 
rm -f add_to_cart.zip 
rm -f checkout_cart.zip
