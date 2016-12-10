# aws_ir-api
A chalice API gateway wrapper around aws_ir.  
**Highly experimental**

## Preparation
1. Create a role to associate with the privileges in this api ( incident-pony-role.json Coming soon. )
2. Deploy that role.  Allow lambda.amazonaws.com to assumerole.  

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}

```

## Getting Started with aws_ir-api

1. Checkout aws_ir git submodule `git submodule update`
2. Install the requirements for the chalice project `pip install -r aws_ir-api/requirements.txt`
3. Install aws_ir requirements `pip install -r aws_ir-api/aws_ir/requirements.txt
4. Run from within __aws_ir-api__ `chalice deploy` 
