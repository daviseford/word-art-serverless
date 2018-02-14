## Word Art Serverless Endpoint

### Requires Docker

### Requires Python 2.7

First, take care of the requirements:

1. `pip install -r requirements.txt`

2. `brew install caskformula/caskformula/inkscape`


### Commands

`sls plugin install -n serverless-python-requirements`

`sls deploy`

`sls logs -f app --tail`

`sls deploy && sls logs -f app --tail`


### Application flow

1. POST Request to [the endpoint](https://gy2aa8c57c.execute-api.us-east-1.amazonaws.com/dev)

```bash
POST /dev HTTP/1.1
Host: gy2aa8c57c.execute-api.us-east-1.amazonaws.com
Content-Type: application/json
Cache-Control: no-cache
Postman-Token: 87c7679b-0719-608d-016a-f10e6f00b276

{
	"text" : "I guess various sentences may lead to various structures. 
	          A short one. Then a quick twist and run, further than we'd anticipated. 
	          I guess. Well, I know that one thing is for certain - long, 
	          run on sentences have a place here. But! So do quick ones. Tight little turns. 
	          Another tactic would be to send out a long, long sentence, broken up by not 
	          much else other than the occasional - well, yes, that - out of nowhere, how surprising. 
	          The more sentences, the merrier. Try giving me a whole book :)"
}
```

2. The `text` is converted into an XML Path.

3. The XML Path is converted into a full SVG file using `svgpathtools`.

4. The contents of the file are checksummed using `sha1` and named `[file-checksum].svg`

5. The file is uploaded to S3. There is a check to ensure we do not upload duplicate files - hence the checksumming.

6. The file's URL is returned as a JSON response like so: `{ 'statusCode': 200, 'body': {"s3_url": "https://s3.amazonaws.com/word-art-svgs/f3f5ea8d8cd19705f3d743c8897eddf0c0e3840a.svg"}`