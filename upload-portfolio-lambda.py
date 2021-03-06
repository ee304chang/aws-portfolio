import boto3
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    sns = boto3.resource('sns')

    try:
        portfolio_bucket = s3.Bucket('adelyn.cc')
        portfolio_zip = StringIO.StringIO()
        topic = sns.Topic('arn:aws:sns:us-west-2:900673541536:portfolio_updated')

        build_bucket = s3.Bucket('portfolio.adelyn.cc')
        build_bucket.download_fileobj('portfolio.zip', portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm,
                    ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        print "Uploaded."
        topic.publish(Subject="Portfolio updated!", Message="Your serverless structured portfolio has been updated.")

    except:
        topic.publish(Subject="Portfolio deploy failed", Message="The portfolio deployment failed.")
