# Project overview

In this project, we can tag almost all aws services within the specific tag like
{
    "Author": "Dong Giang Thai"
}

# Set up environment

## Install Python

* Go to [Download](https://www.python.org/downloads/) page and select the Python version you want.
* Follow the GUI instruction to install if you are on Windows.
* This is the step for Linux user:
  * Update and upgrade your distribution (assume for Debian distribution): `sudo apt update && sudo apt upgrade -y`
  * Install dependencies for installing Python (assume for Debian distribution): `sudo apt install libssl-dev libncurses5-dev libsqlite3-dev libreadline-dev libtk8.6 libgdm-dev libdb4o-cil-dev libpcap-dev`
  * Download the file that called `XZ compressed source tarball` of the Operating System `Source release`. Here is an example link:
    https://www.python.org/ftp/python/3.10.11/Python-3.10.11.tar.xz. Run command `wget --quite --show-progress https://www.python.org/ftp/python/3.10.11/Python-3.10.11.tar.xz` to download the source.
  * Using tar to extract the downloaded file: `tar xvf Python-3.10.11.tar.xz`
  * Change directory into the extracted file: `cd Python-3.10.11`
  * Config the Makefile prepare to install: `./configure`
  * Run the Makefile to set up necessary things: `make`
  * Now install python. You have two options to do this:
    * First - regularly installation that could override the existing Python: `make install`
    * Second - keep the existing Python and install the new one: `make altinstall`
  * Verify the installation by `python3 --version`

## Create virtual environment

* Moving into the project directory
* Install virtualenv: `python3 -m pip install --user virtualenv`
* Create environment: `virtualenv .pyscripts --python python3`
* Activate the environment:
  * With Windows user: `.pyscripts/Script/activate`
  * With Linux user: `. .pyscripts/bin/activate`
* Install all project dependencies: `pip install -r requirements.txt`

## Create account detail file for the configuration

This project uses the Boto3 Session to get the AWS local credentials which is store at `~/.aws/credentials` or `%USERPROFILE%\.aws\credentials`.
Make sure to have your credential in this file.

#### Create accounts-detail.json

Placeholder:
```json lines
{
  <aws-account-id>: {
    "Account Name": <aws-profile-name>,
    "Key Tag": <key-tag>,
    "Value Tag": <value-tag>
  }
}
```
Example `accounts-detail.json`:
```json lines
{
  "111111111111": {
    "Account Name": "Account1 PROD",
    "Key Tag": "Author",
    "Value Tag": "Dong Giang Thai"

  },
  "222222222222": {
    "Account Name": "Account2 PROD",
    "Key Tag": "Language",
    "Value Tag": "Python"
  },
  "333333333333": {
    "Account Name": "Account3 PROD",
    "Key Tag": "JobTitle",
    "Value Tag": "DevOps"
  }
}
```

#### CSV file to extract infor for the tagging job

Recommend creating a folder for all csv files: `mkdir csv`

Placeholder:
```csv
accountId,region,arn,resourceType,tags
<account-id>,<region>,<arn>,<resource-type>,<existing-tag>
```

Example `all_accounts.csv`:
```csv
accountId,region,arn,resourceType,tags
111111111111,"us-east-1","arn:aws:ec2:us-east-1:111111111111:volume/vol-83ru23hf834hsd012","AWS::EC2::Volume","{}"
222222222222,"us-east-1","arn:aws:ec2:us-east-1:222222222222:security-group/sg-83ru23hf834hsd012","AWS::EC2::SecurityGroup","{""App"":""TestAPI"",""Account"":""awsaccountalias"",""Owner"":""DongGiangThai"",""AccountId"":""222222222222"",""IC_Code"":""testapp"",""Config"":""dev"",""Prefix"":""thaidg"",""name"":""use1-thaidg-testapp-eb-sg"",""BuildType"":""terraform"",""Region"":""us-east-1"",""Environment"":""dev-us-east-1-thaidg"",""RegionShorter"":""use1""}"
333333333333,"us-east-1","arn:aws:lambda:us-east-1:333333333333:function:thaidg-testapp-lambda-ta-appservice-client","AWS::Lambda::Function","{""Account"":""awsaccountalias"",""Owner"":""DongGiangThai"",""AccountId"":""333333333333"",""IC_Code"":""testapp"",""Config"":""dev"",""Prefix"":""thaidg"",""Name"":""Lambda.TA.AppServiceClient"",""Function Handler"":""Lambda.TA.AppServiceClient::Lambda.TA.AppServiceClient.Function::FunctionHandler"",""BuildType"":""terraform"",""Environment"":""dev-us-east-1-thaidg"",""Region"":""us-east-1"",""RegionShorter"":""use1"",""Application"":""appservice""}"
```

# Run application

* Open terminal at project directory and run command: `python3 tag_all.py --file-name .\csv\all_accounts.csv --accounts-detail-file .\accounts-detail.json`