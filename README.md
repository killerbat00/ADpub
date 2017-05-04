# :green_book: ADpub - A Serverless Publishing Service :book:

ADpub is a simple publishing service written using Python and [chalice](https://github.com/awslabs/chalice) and deployed to AWS Lambda.

## Features
As a simple API service returning JSON, ADpub aims to do only 3 things:
1. Provide a simple service status page.
2. Creatively consume a publicly available API.
3. Accept PNG uploads that are stored to S3 and published.

The raw data from the API can currently be consumed directly by making HTTP requests to the endpoints specified below.

To discover the services available with ADpub, see [Available Services](#available-services)
To learn more about using ADpub, see [Using ADpub](#using-adpub)

## Available Services
To access the service endpoints, ADpub must be deployed using chalice. See [Using ADpub](#using-adpub) for more information on deployment.

### 1. `GET /status` - Status Page :ok_hand:
The `/status` endpoint returns a JSON-encoded response of status information about the ADpub service.
If the application has been successfully deployed to AWS, the endpoint will successfully resolve and return an HTTP 200 OK response.

The body of the response from `/status` looks like this:
```javascript
{
    "status": "OK",
    "images_uploaded": "<NUMBER OF PNG IMAGES UPLOADED SO FAR">,
    "deployment_info": {
        "machine": "<DEPLOYED MACHINE TYPE e.g. "i386">",
        "platform": "<DEPLOYED MACHINE PLATFORM>",
        "processor": "<DEPLOYED MACHINE PROCESSOR>"
    }
}
```

The `status` and `images_uploaded` keys return the current status of ADpub as well as the number of PNG images uploaded to the service so far.
The value of the `deployment_info` key contains a dictionary of information about the current machine on which ADpub is deployed.

Note: Currently, the value of `status` will always be OK if the `/status` endpoint can be successfully resolved. A failed HTTP response from `/status` should be interpreted as the ADpub service being down. Why? To properly monitor the status of an API service, it's generally necessary to have another machine in addition to the API server that pings the application periodically and keeps track of the application's response. This way, a disruption in the original API service will not prevent users from being able to check the current status of the service. This is currently out of scope for ADpub.

### 2. `GET /breweries` - Creative consumption of a publicly available API :beer:
The `/breweries` endpoint combines two publicly available APIs to return a JSON-encoded response of craft beer breweries near the user.
The IP address of the request to `/breweries` is supplied to [ip-api.com](http://ip-api.com)'s IP Geolocation API to determine the location of the user.
This location information is then passed to [BreweryDB](www.brewerydb.com)'s API to query for craft beer breweries local to that location.
This list of breweries is then returned in a JSON object as the response to `/breweries`.

The body of the response from `/breweries` looks like this:
```javascript
{
    "status": "OK",
    "data": [
        {
            "name": "<BREWERY NAME>",
            "website": "<BREWERY WEBSITE>",
            "phone": "<BREWERY PHONE NUMBER>",
            "street_address": "<BREWERY ADDRESS>",
            "postal_code": "<BREWERY POSTAL CODE>"
        },
        ...
    ]
}
````

If any errors occur while attempting the geolocation of the request's IP address or the brewery lookup, the `status` key will have a value of `"failure"` and no other keys will be set in the response.


### 3. `POST /image` - PNG upload :camera:
The `/image` endpoint is the only endpoint to accept an HTTP POST request.
This endpoint enables users to upload a PNG image to the ADpub service.
When an image is uploaded, the count of images returned by the `/status` endpoint is incremented and a JSON-encoded response of the upload results is returned.

The body of a successful upload response from `/image` looks like this:
````javascript
{
    "status": "OK",
    "data": {
        "URL": "<S3 URL FOR IMAGE>"
    }
}
````

If any errors occur while attempting to upload the image, the `status` key will have a value of `"failure"` and no other keys will be set in the response.

Images uploaded through `/image` must be *.png images. Other filetypes will not be uploaded and will result in a `"failure"` `status` in the response.

### Other endpoints
Requests to endpoints not specified above will request in an HTTP 500 error.

## Using ADpub
Since ADpub uses the [chalice](https://github.com/awslabs/chalice) framework, it runs on AWS Lambda.

A deployed and running version of the ADpub service is currently available at: [link](URL)
If you would like to deploy ADpub to your own AWS account, follow instructions below for [Installing ADpub](#installing-adpub-on-linux)

### Interacting with ADpub
You can use `curl`, [`httpie`](https://github.com/jkbrzt/httpie) or your favorite HTTP client to interact with the services on ADpub.

The following guide, however, will use `httpie` for interaction. You can install `httpie` using `pip install httpie`.

1. Retrieving the current status.
To retrieve the current status of ADpub, point your HTTP client to the `/status` endpoint.
````
$ http https://<ADpub URL>/status
HTTP/1.1 200 OK


{
    "status": "OK",
    "images_uploaded": "<NUMBER OF PNG IMAGES UPLOADED SO FAR">,
    "deployment_info": {
        "machine": "<DEPLOYED MACHINE TYPE e.g. "i386">",
        "platform": "<DEPLOYED MACHINE PLATFORM>",
        "processor": "<DEPLOYED MACHINE PROCESSOR>"
    }
}
````
2. Finding local breweries.
To find local breweries, point your HTTP client to the `/breweries` endpoint.
````
$ http https://<ADpub URL>/breweries
HTTP/1.1 200 OK


{
    "status": "OK",
    "data": [
        {
            "name": "<BREWERY NAME>",
            "website": "<BREWERY WEBSITE>",
            "phone": "<BREWERY PHONE NUMBER>",
            "street_address": "<BREWERY ADDRESS>",
            "postal_code": "<BREWERY POSTAL CODE>"
        },
        ...
    ]
}
````

If ADpub was unable to geolocate the IP address, or lookup breweries close to that IP, the response will look like this:
````
$ http https://<ADpub URL>/breweries
HTTP/1.1 200 OK

{
    "status": "failure"
}
````
3. Uploading an image.
To upload an image to ADpub, send a POST request with your HTTP client to the `/image` endpoint.
This POST request should have a `Content-Type: application/json` and the base64 encoded PNG image should be stored in the `data` key of the JSON request body.

For example:
````
$ http POST https://<ADpub URL>/breweries data=$(base64 -i <PNG IMAGE>)
HTTP/1.1 200 OK

{
    "status": "OK",
    "data": {
        "URL": "<S3 URL FOR IMAGE>"
    }
}
````

If the supplied image was not a PNG image or ADpub was not able to upload the image, the response will look like this:
````
$ http POST https://<ADpub URL>/breweries data=$(base64 -i <JPG IMAGE>)
HTTP/1.1 200 OK

{
    "status": "failure",
}
````

### Installing ADpub on Linux
A deployed and running version of the ADpub service is currently available at: [link](URL)

To deploy this code directly, you will need to be using Python 3.6 or 2.7 ahd have your AWS credentials correctly configured.

If you have not installed the AWS CLI, execute the following commands in a terminal:
````
$ mkdir ~/.aws
$ cat >> ~/.aws/config
[default]
aws_access_key_id=YOUR_ACCESS_KEY_HERE  
aws_secret_access_key=YOUR_SECRET_ACCESS_KEY  
region=YOUR_REGION (such as us-west-2, us-west-1, etc)  
````

Next, clone this repo:
`$ git clone https://github.com/killerbat00/ADpub`

Create a new virtualenv if necessary:
````
$ pip install virtualenv
$ virtualenv ~/.virtualenvs/ADpub
$ source ~/.virtualenvs/ADpub activate
````

Install ADpub using `pip`:
````
$ cd <ADpub DIRECTORY>
$ pip install -r requirements.txt
````

ADpub and chalice are now installed on your machine.

In order to use the `/breweries` endpoint correctly, you will need an API key from BreweryDB.
You can do so by signing up at [BreweryDB.com/developers](www.brewerydb.com/developers/apps)
Once you have registered a new application and obtained an API key, copy it into the `adpub/brewery_key.txt` file in the adpub repo.

### Deploying ADpub
You have two options when it comes to deployment, deploying to AWS Lambda, or deploying to your local machine.

To deploy ADpub to AWS lambda from the ADpub project directory:
`$ chalice deploy`
This command will deploy the application and print a URL for you to use when interacting with the API, see [Interacting with ADpub](#interacting-with-adpub)

To deploy ADpub locally from the ADpub project directory:
`$ chalice local`
This command deploys the application locally and allows you to test using `localhost:8000` as the URL.

### Testing ADpub
ADpub comes with a suite of unittests that ensure it is functioning correctly. These tests are in the [test](/tests) directory of the repo.

To run the test suite, execute `python -m unittest`  from the ADpub project directory.

