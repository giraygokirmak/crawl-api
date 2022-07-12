# crawl-api
To run Web App directly:
docker run -itd --name crawl-api -p 5000:5000 --restart always --env="mongourl=MONGO.SERVER.HOSTNAME" --env="username=KULLANICIADI" --env="password=SIFRE" crawl-api

To scale up for increasing load:
Deploy multiple direct nodes into a cluster and, deploy nginx with tutorial:
http://nginx.org/en/docs/http/load_balancing.html#:~:text=It%20is%20possible%20to%20use,of%20web%20applications%20with%20nginx.
