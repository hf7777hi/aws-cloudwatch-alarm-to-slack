# cloudwatch-alarm-to-slack

ディレクトリ構成は以下の通りになってます。

```bash
.
├── README.md                   <-- This instructions file
├── event.json                  <-- SNS event payload
├── src                         <-- Source code for a lambda function
│   ├── __init__.py
│   ├── app.py                  <-- Lambda function code
└── template.yaml               <-- SAM Template
```

## 環境
以下インストール済みであること
* [Python 3 installed](https://www.python.org/downloads/)
* [aws-sam-cli](https://pypi.org/project/aws-sam-cli/)
* [Docker installed](https://www.docker.com/community-edition)
* AWSCLIの設定(aws configure)も必須です。
    * https://docs.aws.amazon.com/ja_jp/cli/latest/userguide/cli-chap-configure.html#cli-quick-configuration

## 設定
* SLACK_CHANNEL : 投稿するslackのチャンネル名を設定ください。
* ENCRYPTED_INCOMING_TOKEN : 以下コマンドにて暗号化したtokenを設定ください。

```
$ aws kms encrypt --key-id alias/[key名] --plaintext "[token(https://hooks.slack.com/services/以下の部分)]"
```

## テスト実行

```bash
sam local invoke --e event.json
```

テスト実行する際は、event.jsonのMessageを変更で可能です。

## アラーム設定
template.yamlに設定するか、ソースをデプロイした後手動で設定してください。

参考 : https://docs.aws.amazon.com/ja_jp/AWSCloudFormation/latest/UserGuide/aws-properties-cw-alarm.html

## デプロイ 
### S3作成
Lambda関数をアップロードするためのS3バケットを作成します（初回のみ）。

```bash
aws s3 mb s3://BUCKET_NAME
```

### S3にソースをアップロード
以下コマンドでS3バケットにソースをアップロードします。

```bash
sam package \
    --output-template-file packaged.yaml \
    --s3-bucket REPLACE_THIS_WITH_YOUR_S3_BUCKET_NAME
```

### Cloudformation Stackにデプロイ

```bash
sam deploy \
    --template-file packaged.yaml \
    --stack-name cloudwatch-alarm-to-slack \
    --capabilities CAPABILITY_IAM
```



> **See [Serverless Application Model (SAM) HOWTO Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-quick-start.html) for more details in how to get started.**


## SAM and AWS CLI commands

All commands used throughout this document

```bash
# Generate event.json via generate-event command
sam local generate-event apigateway aws-proxy > event.json

# Invoke function locally with event.json as an input
sam local invoke HelloWorldFunction --event event.json

# Run API Gateway locally
sam local start-api

# Create S3 bucket
aws s3 mb s3://BUCKET_NAME

# Package Lambda function defined locally and upload to S3 as an artifact
sam package \
    --output-template-file packaged.yaml \
    --s3-bucket REPLACE_THIS_WITH_YOUR_S3_BUCKET_NAME

# Deploy SAM template as a CloudFormation stack
sam deploy \
    --template-file packaged.yaml \
    --stack-name cloudwatch-alarm-to-slack \
    --capabilities CAPABILITY_IAM

# Describe Output section of CloudFormation stack previously created
aws cloudformation describe-stacks \
    --stack-name cloudwatch-alarm-to-slack \
    --query 'Stacks[].Outputs[?OutputKey==`HelloWorldApi`]' \
    --output table

# Tail Lambda function Logs using Logical name defined in SAM Template
sam logs -n HelloWorldFunction --stack-name cloudwatch-alarm-to-slack --tail
```

