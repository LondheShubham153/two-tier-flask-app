# Two Tier application execution steps

1. Clone code to local received from dev team
```sh
git clone <url>
```
2.  Create DockerFile
3.  Create new network
```sh
docker network create twotire
```
> as type of network is not mentioned it will generate with bridge as its default network

3.  Run available image for sql and also add network for communication between msql and flask, env variable as per application  and also add volume to persist data 
```sh
docker run -d --name mysql_data_with_vloume -v mysql_volume_1:/var/lib/mysql --network twotire -e MYSQL_DATABASE=devops -e MYSQL_ROOT_PASSWORD=root mysql:5.7
```
> [-d](): Run container in demon/background mode
>
> [--name mysql_data_with_vloume](): it sets the name for generated container
>
> [-v mysql_volume_1:/var/lib/mysql](): it will create mysql_volume_1 named volume and mount to  /var/lib/mysql location
>
> [--network twotire](): It will set user-generated bridge network for communication between db and flask
>
> [-e MYSQL_DATABASE=devops](): -e can be while setting env varibale -e <variable name>=<value>
>
> [mysql:5.7](): <image name>:tag


4. Build docker image for flask
```sh
docker build -t two_tire_app:latest
```

5. Run docker image
```sh
docker run -d --network twotire --name two-tire-application -p 5000:5000 -e MYSQL_HOST=mysql_data_with_vloume -e MYSQL_USER=root -e MYSQL_PASSWORD=root -e MYSQL_DB=devops two_tire_app:latest
```
`Note`: the element explain above is not explained again 
>[-p 5000:5000](): It will expose port 5000 to run application 

6. EC2 UI , In the security group edit inbound rule for port 5000
7. run <ip address>:5000 in browser
8. To validate data entered in DB 
   A. use execute cmd to run MySQL in local
     ```sh
     docker exec -it mysql_data_with_vloume bash
     ```
    >[-it mysql_data_with_vloume]():add docker container name for mysql
 
     B. Switch bash CLI to Mysql
     ```sh
     mysql -u <uname> -p
     ```
     C. switch to our application database 
     ```sh
     use <database name>;
     ```
     D. List of tabels
     ```sh
     show tabels;
     ```
     E. Get all entered data from tabel 
     ```sh
     select * from <tabel name>;
     ```
     
