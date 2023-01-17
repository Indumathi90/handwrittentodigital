# handwrittentodigital

This online convertor uses Azure computer vision API to convert handwritten text images to digital text content.

To run this locally, set the below environment variables

* COMPUTER_VISION_KEY
* COMPUTER_VISION_NAME

```
set COMPUTER_VISION_KEY=<key>
set COMPUTER_VISION_NAME=<name>
```

### Set up

1. Open command prompt or terminal
2. Create python virtual environment
   `python -m venv virtualenv`
3. Activate python virtual environment

   ```
   .\virtualenv\Scripts\activate
   
      or
   
   cd virtualenv\Scripts
   activate
   cd ../..
   ```
4. Install requirements
   `pip install -r requirements.txt`

### Run application
Set the environment variables mentioned above
`flask --app controller run`
