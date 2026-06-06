# Launch public EC2 demo for PITER AiOps mid-project.
# Usage: .\scripts\launch_ec2_demo.ps1
$ErrorActionPreference = "Stop"
$Profile = if ($env:AWS_PROFILE) { $env:AWS_PROFILE } else { "reemmor" }
$Region = "us-east-1"
$ProjectRoot = Split-Path $PSScriptRoot -Parent

function Invoke-Aws {
  param([string[]]$AwsArgs)
  & aws @AwsArgs --profile $Profile --region $Region
  if ($LASTEXITCODE -ne 0) { throw "aws failed: $($AwsArgs -join ' ')" }
}

$ami = (Invoke-Aws @(
  "ec2", "describe-images", "--owners", "amazon",
  "--filters", "Name=name,Values=al2023-ami-2023.*-kernel-6.1-x86_64", "Name=state,Values=available",
  "--query", "sort_by(Images,&CreationDate)[-1].ImageId", "--output", "text"
)).Trim()
if (-not $ami -or $ami -eq "None") {
  $ami = "ami-00e801948462f718a"
}

$myIp = (Invoke-RestMethod -Uri "https://checkip.amazonaws.com").Trim()
$cidr = "$myIp/32"

$sgName = "piter-aiops-sg"
$sgId = (Invoke-Aws @(
  "ec2", "describe-security-groups", "--filters", "Name=group-name,Values=$sgName",
  "--query", "SecurityGroups[0].GroupId", "--output", "text"
)).Trim()

if (-not $sgId -or $sgId -eq "None") {
  $vpc = (Invoke-Aws @(
    "ec2", "describe-vpcs", "--filters", "Name=isDefault,Values=true",
    "--query", "Vpcs[0].VpcId", "--output", "text"
  )).Trim()
  $sgId = (Invoke-Aws @(
    "ec2", "create-security-group", "--group-name", $sgName,
    "--description", "PITER AiOps midproject demo", "--vpc-id", $vpc,
    "--query", "GroupId", "--output", "text"
  )).Trim()
  Invoke-Aws @(
    "ec2", "authorize-security-group-ingress", "--group-id", $sgId,
    "--ip-permissions",
    "IpProtocol=tcp,FromPort=8080,ToPort=8080,IpRanges=[{CidrIp=0.0.0.0/0}]",
    "IpProtocol=tcp,FromPort=22,ToPort=22,IpRanges=[{CidrIp=$cidr}]"
  ) | Out-Null
}

$userDataPath = Join-Path $ProjectRoot "infra\ec2_user_data_demo.sh"
$userData = Get-Content $userDataPath -Raw
$secret = -join ((48..57) + (97..102) | Get-Random -Count 64 | ForEach-Object { [char]$_ })
$userData = $userData.Replace("__FLASK_SECRET__", $secret)
$userDataB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($userData))

$tagJson = "ResourceType=instance,Tags=[{Key=Name,Value=piter-aiops-demo},{Key=Project,Value=piter-aiops},{Key=Owner,Value=reemmor}]"
$instanceId = (Invoke-Aws @(
  "ec2", "run-instances",
  "--image-id", $ami,
  "--instance-type", "t3.micro",
  "--key-name", "amdocs-course-key",
  "--security-group-ids", $sgId,
  "--iam-instance-profile", "Name=IncidentRagBedrockEC2Profile",
  "--user-data", $userDataB64,
  "--tag-specifications", $tagJson,
  "--query", "Instances[0].InstanceId",
  "--output", "text"
)).Trim()

Write-Host "Launched $instanceId - waiting for running..."
Invoke-Aws @("ec2", "wait", "instance-running", "--instance-ids", $instanceId) | Out-Null
$ip = (Invoke-Aws @(
  "ec2", "describe-instances", "--instance-ids", $instanceId,
  "--query", "Reservations[0].Instances[0].PublicIpAddress", "--output", "text"
)).Trim()

Write-Host ('Public URL: http://{0}:8080/' -f $ip)
Write-Host ('InstanceId: {0}' -f $instanceId)
Write-Host ('SecurityGroup: {0}' -f $sgId)
Write-Host 'Wait 3-5 min for user-data docker pull, then open URL.'
